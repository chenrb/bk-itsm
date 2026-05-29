# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2025 Tencent.  All rights reserved.

BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.

License for BK-ITSM 蓝鲸流程服务:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps

from django.conf import settings

from common.log import logger
from itsm.ticket.models import Ticket
from pipeline.engine.models import Data, ScheduleService, Status, PipelineProcess


def time_this_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        end = datetime.now()
        print((func.__name__, (end - start).seconds))
        return result

    return wrapper


@dataclass
class AutoSchedules:
    """API 节点卡顿任务"""

    timeout_minutes: int = settings.AUTO_TIMEOUT_MINUTES

    def __post_init__(self):
        if not isinstance(self.timeout_minutes, int) or self.timeout_minutes <= 0:
            self.timeout_minutes = 30

    def find_stuck_schedules(self) -> list:
        stuck_schedules = []
        now = datetime.now()
        timeout_threshold = now - timedelta(minutes=self.timeout_minutes)

        schedules = ScheduleService.objects.filter(
            is_finished=False,
            wait_callback=False,
        ).select_related()

        logger.info(f"共有 {schedules.count()} 个未完成的轮询型调度任务")

        process_ids = list(schedules.values_list("process_id", flat=True))
        ticket_info_map = self._batch_get_ticket_info(process_ids)

        for ss in schedules:
            try:
                status = Status.objects.filter(id=ss.activity_id).first()
                if not status:
                    continue

                if status.state != "RUNNING":
                    continue

                data = Data.objects.filter(id=ss.activity_id).first()
                if not data:
                    continue

                outputs = data.outputs or {}
                if isinstance(outputs, str):
                    try:
                        outputs = json.loads(outputs)
                    except json.JSONDecodeError:
                        continue

                if outputs.get("service_status"):
                    continue

                poll_time = outputs.get("poll_time", 0)
                poll_interval = outputs.get("poll_interval", 0)
                latest_poll_time_str = outputs.get("latest_poll_time")

                if not poll_time or poll_time <= 0:
                    continue
                if not poll_interval or poll_interval <= 0:
                    continue

                latest_poll_time = self._parse_datetime(latest_poll_time_str)

                if latest_poll_time:
                    is_stuck, minutes_overdue, next_poll_time, reason = self._check_stuck_condition(
                        latest_poll_time, poll_interval, status.started_time, now, timeout_threshold
                    )

                    if is_stuck:
                        ticket_id, service_id = ticket_info_map.get(ss.process_id, (None, None))
                        stuck_schedules.append(
                            self._build_stuck_schedule_info(ss, status, ticket_id, service_id,
                                                            poll_time, poll_interval,
                                                            latest_poll_time, next_poll_time,
                                                            minutes_overdue, reason)
                        )

            except Exception as e:
                logger.error(f"处理 schedule {ss.id} 时出错: {e}")
                continue
        stuck_schedules.sort(key=lambda x: x["minutes_overdue"], reverse=True)
        return stuck_schedules

    def fix_stuck_schedules(self, stuck_schedules: list) -> tuple[int, int]:
        logger.info("\n开始修复卡住的调度任务...")
        fixed_count = 0
        failed_count = 0

        for item in stuck_schedules:
            schedule_id = item["schedule_id"]
            process_id = item["process_id"]
            try:
                res = self._fix_core_schedules(schedule_id, process_id)
                if res:
                    fixed_count += 1
            except Exception as e:
                logger.error(f"  修复 schedule {schedule_id} 失败: {e}")
                failed_count += 1

        logger.info(f"\n修复完成: 成功 {fixed_count} 个, 失败 {failed_count} 个")
        return fixed_count, failed_count

    def fix_one_schedule(self, schedule_id, process_id) -> bool:
        try:
            return self._fix_core_schedules(schedule_id, process_id)
        except Exception:
            return False

    @staticmethod
    def _fix_core_schedules(schedule_id: str, process_id: str) -> bool:
        from pipeline.engine import signals
        from pipeline.django_signal_valve import valve

        updated = ScheduleService.objects.filter(
            id=schedule_id, is_scheduling=True
        ).update(is_scheduling=False)

        if updated:
            logger.info(f"已重置 schedule {schedule_id} 的 is_scheduling 锁")

        sched_service = ScheduleService.objects.get(process_id=process_id)

        valve.send(
            signals,
            "schedule_ready",
            sender=ScheduleService,
            process_id=sched_service.process_id,
            schedule_id=sched_service.id,
            countdown=0,
        )

        logger.info(f"  已重新触发 schedule {schedule_id} 的调度")
        return True

    @staticmethod
    def _batch_get_ticket_info(process_ids: list) -> dict:
        result = {}
        if not process_ids:
            return result

        try:
            processes = PipelineProcess.objects.filter(
                id__in=process_ids
            ).values("id", "root_pipeline_id")

            process_to_ticket = {p["id"]: p["root_pipeline_id"] for p in processes}
            ticket_ids = list(set(process_to_ticket.values()))

            tickets = Ticket._objects.filter(
                id__in=ticket_ids
            ).values("id", "service_id")

            ticket_info = {str(t["id"]): t.get("service_id") for t in tickets}

            for process_id, ticket_id in process_to_ticket.items():
                service_id = ticket_info.get(str(ticket_id))
                result[process_id] = (ticket_id, service_id)

        except Exception as e:
            logger.error(f"批量获取 ticket 信息失败: {e}")

        return result

    @staticmethod
    def _check_stuck_condition(
        latest_poll_time, poll_interval, started_time, now, timeout_threshold
    ):
        if latest_poll_time:
            next_poll_time = latest_poll_time + timedelta(seconds=poll_interval)
            if next_poll_time < timeout_threshold:
                minutes_overdue = (now - next_poll_time).total_seconds() / 60
                return True, minutes_overdue, next_poll_time, "latest_poll_time + poll_interval 超时"
        elif started_time and started_time < timeout_threshold:
            minutes_running = (now - started_time.replace(tzinfo=None)).total_seconds() / 60
            return True, minutes_running, None, "无 latest_poll_time 且运行时间超时"
        return False, 0, None, ""

    @staticmethod
    def _parse_datetime(value):
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            for fmt in [
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S",
            ]:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
        return None

    @staticmethod
    def _build_stuck_schedule_info(
        ss, status, ticket_id, service_id, poll_time, poll_interval,
        latest_poll_time, next_poll_time, minutes_overdue, reason
    ):
        return {
            "schedule_id": ss.id,
            "activity_id": ss.activity_id,
            "process_id": ss.process_id,
            "ticket_id": ticket_id,
            "service_id": service_id,
            "schedule_times": ss.schedule_times,
            "is_scheduling": ss.is_scheduling,
            "poll_time": poll_time,
            "poll_interval": poll_interval,
            "latest_poll_time": latest_poll_time,
            "next_poll_time": next_poll_time,
            "started_time": status.started_time,
            "minutes_overdue": minutes_overdue,
            "reason": reason,
        }
