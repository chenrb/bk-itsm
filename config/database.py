# -*- coding: utf-8 -*-
"""缓存 + Redis + 数据后端 + 数据库补丁"""
import os

from django.db.backends.mysql.features import DatabaseFeatures
from django.utils.functional import cached_property

# ==============================================================================
# Cache
# ==============================================================================
REDIS_HOST = os.environ.get("REDIS_HOST")
IS_USE_REDIS = REDIS_HOST is not None

if IS_USE_REDIS:
    REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")
    REDIS_SERVICE_NAME = os.environ.get("REDIS_SERVICE_NAME", "mymaster")
    REDIS_MODE = os.environ.get("REDIS_MODE", "single")
    REDIS_DB = os.environ.get("REDIS_DB", 0)
    REDIS_SENTINEL_PASSWORD = os.environ.get(
        "REDIS_SENTINEL_PASSWORD", REDIS_PASSWORD
    )
    # 哨兵
    replication_caches = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "{}/{}:{}/{}".format(
                REDIS_SERVICE_NAME, REDIS_HOST, REDIS_PORT, REDIS_DB
            ),
            "OPTIONS": {
                "CLIENT_CLASS": "itsm.component.data.sentinel.SentinelClient",
                "PASSWORD": REDIS_PASSWORD,
                "SENTINEL_PASSWORD": REDIS_SENTINEL_PASSWORD,
            },
        },
    }
    # 单机
    single_caches = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://{}:{}/{}".format(REDIS_HOST, REDIS_PORT, REDIS_DB),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "PASSWORD": REDIS_PASSWORD,
            },
        },
    }
    CACHES_GETTER = {"replication": replication_caches, "single": single_caches}
    CACHES = CACHES_GETTER[REDIS_MODE]
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "django_cache",
        }
    }

CACHES.update(
    {
        "db": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "django_cache",
        },
        "login_db": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "account_cache",
        },
        "dummy": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        },
        "locmem": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        },
    }
)

# ==============================================================================
# 数据后端
# ==============================================================================
if IS_USE_REDIS:
    ITSM_DATA_BACKEND = "itsm.component.data.redis_backend.RedisDataBackend"
    PIPELINE_DATA_BACKEND = "pipeline.engine.core.data.redis_backend.RedisDataBackend"
    PIPELINE_DATA_CANDIDATE_BACKEND = os.getenv(
        "PIPELINE_DATA_CANDIDATE_BACKEND",
        "pipeline.engine.core.data.mysql_backend.MySQLDataBackend",
    )
    PIPELINE_DATA_BACKEND_AUTO_EXPIRE = True
else:
    ITSM_DATA_BACKEND = "itsm.component.data.mysql_backend.MySQLDataBackend"
    PIPELINE_DATA_BACKEND = "pipeline.engine.core.data.mysql_backend.MySQLDataBackend"


# ==============================================================================
# Database
# ==============================================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("MYSQL_NAME", "bk_itsm"),
        "USER": os.environ.get("MYSQL_USER", "root"),
        "PASSWORD": os.environ.get("MYSQL_PASSWORD", ""),
        "HOST": os.environ.get("MYSQL_HOST", "localhost"),
        "PORT": os.environ.get("MYSQL_PORT", "3306"),
        "TEST": {
            "NAME": os.environ.get("MYSQL_TEST_NAME", "bk_itsm_test"),
        },
    }
}

# ==============================================================================
# DatabaseFeatures 补丁
# ==============================================================================
class PatchFeatures:
    @cached_property
    def minimum_database_version(self):
        if self.connection.mysql_is_mariadb:
            return (10, 4)
        else:
            return (5, 7)


DatabaseFeatures.minimum_database_version = PatchFeatures.minimum_database_version

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
