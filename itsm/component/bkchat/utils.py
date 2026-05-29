# -*- coding: utf-8 -*-
"""BKChat utility stubs."""
import logging

logger = logging.getLogger("app")


def notify_fast_approval_message(ticket, state_id, receivers):
    logger.warning(
        "notify_fast_approval_message stub called — BKChat decoupled. "
        "ticket=%s, state_id=%s",
        ticket.id if hasattr(ticket, "id") else ticket,
        state_id,
    )


def proceed_fast_approval(request):
    logger.warning("proceed_fast_approval stub called — BKChat decoupled")
    return None


def build_bkchat_summary(ticket):
    logger.warning("build_bkchat_summary stub called — BKChat decoupled")
    return ""
