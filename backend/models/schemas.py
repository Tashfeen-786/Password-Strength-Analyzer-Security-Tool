"""
Pydantic request/response schemas for the REST API (PDF section 23).

Request validation guarantees:
  * password is a string, at most MAX_PASSWORD_LENGTH characters (128)
  * the optional demo context is at most 3 short fields
  * validation errors never echo the password back (handled in app.py)
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from ..utils.config import MAX_PASSWORD_LENGTH


class DemoContext(BaseModel):
    """Optional, voluntary DEMO context (never stored)."""
    first_name: str = Field(default="", max_length=64)
    birth_year: str = Field(default="", max_length=4)
    organization: str = Field(default="", max_length=64)


class PolicyOverrides(BaseModel):
    minimum_length: Optional[int] = Field(default=None, ge=1, le=128)
    common_password_check: Optional[bool] = None
    personal_info_check: Optional[bool] = None
    allow_spaces: Optional[bool] = None


class AnalyzeRequest(BaseModel):
    password: str = Field(..., min_length=0, max_length=MAX_PASSWORD_LENGTH)
    context: Optional[DemoContext] = None
    policy: Optional[PolicyOverrides] = None


class GenerateRequest(BaseModel):
    mode: str = Field(default="password", pattern="^(password|passphrase)$")
    length: int = Field(default=16, ge=8, le=64)
    uppercase: bool = True
    lowercase: bool = True
    numbers: bool = True
    symbols: bool = True
    words: int = Field(default=4, ge=3, le=8)
    separator: str = Field(default="-", max_length=1)
