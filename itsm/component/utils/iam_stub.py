# -*- coding: utf-8 -*-
"""
No-op stub for the removed IAM SDK (iam/) and itsm.auth_iam modules.

Provides ``IamRequest`` with safe defaults so that the rest of the
codebase can import it without pulling in the deleted packages.
"""


class IamRequest:
    """Stub replacement for ``itsm.auth_iam.utils.IamRequest``.

    Every permission check returns "allowed" so that the application
    keeps working in environments where the IAM backend is unavailable.
    """

    def __init__(self, request=None, username=None):
        self.request = request
        self.username = username

    # -- helpers used by callers ----------------------------------------

    def get_apply_url(self, actions, resources=None, system_id=None):
        """Return a placeholder URL for permission application pages."""
        return "#"

    def resource_multi_actions_allowed(self, actions, resources, **kwargs):
        """Return *all* actions as allowed for a single resource."""
        return {action: True for action in actions}

    def batch_resource_multi_actions_allowed(self, actions, resources, **kwargs):
        """Return *all* actions as allowed for every resource.

        The key in the returned dict is ``resource["resource_id"]`` which
        is the convention used throughout the codebase.
        """
        result = {}
        for resource in resources or []:
            resource_id = str(resource.get("resource_id", ""))
            result[resource_id] = {action: True for action in actions}
        return result

    # -- legacy aliases --------------------------------------------------

    def get_project(self, project_key):
        """Compatibility shim – callers import this from the original class."""
        from itsm.project.models import Project

        return Project.objects.get(key=project_key)


def grant_instance_creator_related_actions(instance):
    """No-op stub — IAM grant removed."""
