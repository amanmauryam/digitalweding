"""Private storage for uploaded wedding invitation cards.

Original invitation scans are the most sensitive data in the product: they
usually contain the family address, guest list hints and sometimes the
parents' phone numbers.  They are therefore kept **outside** ``MEDIA_ROOT``
so that Django's development media server can never expose them at a
predictable URL.  Only the owner can reach them through
``websites.views.invitation_source``.
"""

from __future__ import annotations

import os
import re
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage

SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def sanitise_upload_name(filename: str) -> str:
    """Return a safe, collision-proof file name (no path traversal)."""

    base = os.path.basename(filename or "").strip()
    base = SAFE_NAME_RE.sub("-", base).strip("-.")
    if not base:
        base = "upload"
    stem, dot, ext = base.rpartition(".")
    stem = stem[:60] or "upload"
    ext = ext[:10]
    unique = uuid.uuid4().hex[:12]
    return f"{stem}-{unique}{dot}{ext}"


def private_upload_to(instance, filename: str) -> str:
    """``upload_to`` callable storing invitation cards under a random path."""

    owner = getattr(instance, "owner_id", None) or 0
    return f"invitations/{owner}/{sanitise_upload_name(filename)}"


class PrivateFileSystemStorage(FileSystemStorage):
    """FileSystemStorage rooted outside MEDIA_ROOT (never publicly served)."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("location", Path(settings.PRIVATE_UPLOAD_ROOT))
        kwargs.setdefault("base_url", None)
        super().__init__(*args, **kwargs)


private_storage = PrivateFileSystemStorage()
