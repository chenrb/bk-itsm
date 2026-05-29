# -*- coding: utf-8 -*-
"""APIGW client module stub."""
import logging
import warnings

logger = logging.getLogger("app")


class _ServiceStub:
    """Logs a warning and returns empty result for any method call."""

    def __init__(self, name):
        self._name = name

    def __getattr__(self, method):
        def _stub_fn(*args, **kwargs):
            warnings.warn(
                f"APIGW client call {self._name}.{method}() is a stub — "
                "BlueKing API gateway has been decoupled",
                DeprecationWarning,
                stacklevel=2,
            )
            logger.warning("APIGW stub: %s.%s() called", self._name, method)
            return {}

        return _stub_fn


class _ClientStub:
    """Redirects attribute access to service stubs."""

    def __getattr__(self, name):
        return _ServiceStub(name)


client = _ClientStub()
