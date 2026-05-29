# -*- coding: utf-8 -*-
"""Wiki 配置"""
WIKI_MARKDOWN_HTML_WHITELIST = ["center", "style", "div"]
WIKI_MARKDOWN_HTML_ATTRIBUTES = {"*": ["style"]}
WIKI_MARKDOWN_HTML_STYLES = [
    "padding",
    "width",
    "color",
    "float",
    "clear",
    "background",
]

WIKI_ATTACHMENTS_EXTENSIONS = [
    "pdf", "doc", "odt", "docx", "txt",
    "pptx", "ppt", "zip", "gz",
    "jpeg", "jpg", "png", "gif",
]

WIKI_ANONYMOUS = True
WIKI_ACCOUNT_HANDLING = True
WIKI_ACCOUNT_SIGNUP_ALLOWED = False
WIKI_ANONYMOUS_WRITE = False
WIKI_ANONYMOUS_CREATE = False

REVISIONS_PER_MINUTES = 30
REVISIONS_PER_HOUR = REVISIONS_PER_MINUTES * 60

WIKI_EDITOR_INCLUDE_JAVASCRIPT = True

SIMPLEMDE_OPTIONS = {
    "hideIcons": ["guide", "heading"],
    "showIcons": ["heading-2"],
    "promptURLs": True,
    "spellChecker": False,
    "placeholder": "",
    "status": False,
    "autosave": {"enabled": True},
}


def is_owner_or_readonly(article, user):
    if user.is_wiki_superuser:
        return True
    return not user.is_anonymous and user == article.owner


WIKI_CAN_DELETE = is_owner_or_readonly
WIKI_CAN_ASSIGN = is_owner_or_readonly
WIKI_ASSIGN_OWNER = is_owner_or_readonly
WIKI_CAN_CHANGE_PERMISSIONS = is_owner_or_readonly
WIKI_CAN_MODERATE = is_owner_or_readonly
WIKI_CAN_ADMIN = is_owner_or_readonly
