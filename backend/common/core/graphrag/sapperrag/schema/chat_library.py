from __future__ import annotations

from typing import Dict

from pydantic import Field

from backend.common.schema import SchemaBase


class LibraryBase(SchemaBase):
    kg_base_uuid: str | None = Field("")
    name: str | None = Field("")


class LibraryDetail(LibraryBase):
    messages: Dict[str, str] | None = Field("")


class CreateLibraryParam(LibraryBase):
    pass


class UpdateLibraryParam(LibraryDetail):
    pass