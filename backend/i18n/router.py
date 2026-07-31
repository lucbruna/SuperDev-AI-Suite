"""Internationalization API routes."""

from __future__ import annotations

from typing import Any

from backend.dependencies import get_current_active_user
from backend.i18n.translations import i18n
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

router = APIRouter(dependencies=[Depends(get_current_active_user)])


class TranslateRequest(BaseModel):
    key: str
    locale: str | None = None
    variables: dict[str, Any] = {}


class SetLocaleRequest(BaseModel):
    locale: str


class LoadTranslationsRequest(BaseModel):
    locale: str
    translations: dict[str, str]


@router.get("/locales")
async def list_locales(
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    return {
        "current": i18n._current_locale,
        "fallback": i18n._fallback_locale,
        "supported": i18n.get_supported_locales(),
    }


@router.post("/translate")
async def translate(
    request: TranslateRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, str]:
    result = i18n.t(request.key, locale=request.locale, **request.variables)
    return {"key": request.key, "translation": result, "locale": request.locale or i18n._current_locale}


@router.post("/locale")
async def set_locale(
    request: SetLocaleRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, str]:
    i18n.set_locale(request.locale)
    return {"locale": i18n._current_locale}


@router.post("/translations/{locale}")
async def load_translations(
    locale: str,
    request: LoadTranslationsRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    ts = i18n._translations.get(locale)
    if ts:
        ts.translations.update(request.translations)
    else:
        from backend.i18n.translations import TranslationSet
        i18n._translations[locale] = TranslationSet(
            locale=locale, translations=request.translations
        )
    return {"locale": locale, "count": len(request.translations)}


@router.get("/translations/{locale}")
async def get_translations(
    locale: str,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, str]:
    translations = i18n.export_translations(locale)
    if translations is None:
        return {}
    return translations


@router.get("/missing/{locale}")
async def get_missing_keys(
    locale: str,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    missing = i18n.get_missing_keys(locale)
    return {"locale": locale, "missing_keys": missing, "count": len(missing)}


@router.get("/stats")
async def i18n_stats(
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    return i18n.get_stats()
