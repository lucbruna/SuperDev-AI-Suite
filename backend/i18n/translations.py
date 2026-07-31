"""Internationalization (i18n) service with translation support."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TranslationSet:
    locale: str
    translations: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class I18nService:
    """Internationalization service supporting multiple locales."""

    DEFAULT_LOCALE = "en"
    SUPPORTED_LOCALES = ["en", "pt-BR", "es", "fr", "de", "ja", "zh"]

    def __init__(self):
        self._translations: dict[str, TranslationSet] = {}
        self._current_locale: str = self.DEFAULT_LOCALE
        self._fallback_locale: str = self.DEFAULT_LOCALE
        self._load_default_translations()

    def _load_default_translations(self) -> None:
        self._translations["en"] = TranslationSet(
            locale="en",
            translations={
                "common.save": "Save",
                "common.cancel": "Cancel",
                "common.delete": "Delete",
                "common.edit": "Edit",
                "common.create": "Create",
                "common.search": "Search",
                "common.loading": "Loading...",
                "common.error": "Error",
                "common.success": "Success",
                "common.warning": "Warning",
                "common.confirm": "Confirm",
                "common.back": "Back",
                "common.next": "Next",
                "common.submit": "Submit",
                "common.close": "Close",
                "common.yes": "Yes",
                "common.no": "No",
                "auth.login": "Login",
                "auth.logout": "Logout",
                "auth.register": "Register",
                "auth.forgot_password": "Forgot password?",
                "auth.reset_password": "Reset password",
                "auth.email": "Email",
                "auth.password": "Password",
                "auth.confirm_password": "Confirm password",
                "auth.welcome": "Welcome",
                "auth.invalid_credentials": "Invalid email or password",
                "auth.account_locked": "Account locked due to too many failed attempts",
                "user.profile": "Profile",
                "user.settings": "Settings",
                "user.name": "Name",
                "user.email": "Email",
                "user.avatar": "Avatar",
                "user.role": "Role",
                "user.created_at": "Created at",
                "user.updated_at": "Updated at",
                "project.name": "Project name",
                "project.description": "Description",
                "project.members": "Members",
                "project.settings": "Settings",
                "notification.title": "Title",
                "notification.message": "Message",
                "notification.mark_read": "Mark as read",
                "notification.mark_all_read": "Mark all as read",
                "error.not_found": "Resource not found",
                "error.unauthorized": "Unauthorized",
                "error.forbidden": "Forbidden",
                "error.server_error": "Internal server error",
                "error.bad_request": "Bad request",
                "error.conflict": "Resource already exists",
                "error.validation": "Validation error",
            },
        )

        self._translations["pt-BR"] = TranslationSet(
            locale="pt-BR",
            translations={
                "common.save": "Salvar",
                "common.cancel": "Cancelar",
                "common.delete": "Excluir",
                "common.edit": "Editar",
                "common.create": "Criar",
                "common.search": "Buscar",
                "common.loading": "Carregando...",
                "common.error": "Erro",
                "common.success": "Sucesso",
                "common.warning": "Aviso",
                "common.confirm": "Confirmar",
                "common.back": "Voltar",
                "common.next": "Proximo",
                "common.submit": "Enviar",
                "common.close": "Fechar",
                "common.yes": "Sim",
                "common.no": "Nao",
                "auth.login": "Entrar",
                "auth.logout": "Sair",
                "auth.register": "Registrar",
                "auth.forgot_password": "Esqueceu a senha?",
                "auth.reset_password": "Redefinir senha",
                "auth.email": "E-mail",
                "auth.password": "Senha",
                "auth.confirm_password": "Confirmar senha",
                "auth.welcome": "Bem-vindo",
                "auth.invalid_credentials": "E-mail ou senha invalidos",
                "auth.account_locked": "Conta bloqueada por excesso de tentativas",
                "user.profile": "Perfil",
                "user.settings": "Configuracoes",
                "user.name": "Nome",
                "user.email": "E-mail",
                "user.avatar": "Avatar",
                "user.role": "Funcao",
                "user.created_at": "Criado em",
                "user.updated_at": "Atualizado em",
                "project.name": "Nome do projeto",
                "project.description": "Descricao",
                "project.members": "Membros",
                "project.settings": "Configuracoes",
                "notification.title": "Titulo",
                "notification.message": "Mensagem",
                "notification.mark_read": "Marcar como lida",
                "notification.mark_all_read": "Marcar todas como lidas",
                "error.not_found": "Recurso nao encontrado",
                "error.unauthorized": "Nao autorizado",
                "error.forbidden": "Proibido",
                "error.server_error": "Erro interno do servidor",
                "error.bad_request": "Requisicao invalida",
                "error.conflict": "Recurso ja existe",
                "error.validation": "Erro de validacao",
            },
        )

        self._translations["es"] = TranslationSet(
            locale="es",
            translations={
                "common.save": "Guardar",
                "common.cancel": "Cancelar",
                "common.delete": "Eliminar",
                "common.edit": "Editar",
                "common.create": "Crear",
                "common.search": "Buscar",
                "common.loading": "Cargando...",
                "common.error": "Error",
                "common.success": "Exito",
                "common.warning": "Advertencia",
                "common.confirm": "Confirmar",
                "auth.login": "Iniciar sesion",
                "auth.logout": "Cerrar sesion",
                "auth.register": "Registrarse",
                "auth.email": "Correo electronico",
                "auth.password": "Contrasena",
                "auth.welcome": "Bienvenido",
                "error.not_found": "Recurso no encontrado",
                "error.unauthorized": "No autorizado",
                "error.forbidden": "Prohibido",
                "error.server_error": "Error interno del servidor",
            },
        )

        self._translations["fr"] = TranslationSet(
            locale="fr",
            translations={
                "common.save": "Enregistrer",
                "common.cancel": "Annuler",
                "common.delete": "Supprimer",
                "common.edit": "Modifier",
                "common.create": "Creer",
                "common.search": "Rechercher",
                "common.loading": "Chargement...",
                "common.error": "Erreur",
                "common.success": "Succes",
                "auth.login": "Connexion",
                "auth.logout": "Deconnexion",
                "auth.register": "S'inscrire",
                "auth.email": "E-mail",
                "auth.password": "Mot de passe",
                "error.not_found": "Ressource non trouvee",
                "error.unauthorized": "Non autorise",
            },
        )

        self._translations["de"] = TranslationSet(
            locale="de",
            translations={
                "common.save": "Speichern",
                "common.cancel": "Abbrechen",
                "common.delete": "Loschen",
                "common.edit": "Bearbeiten",
                "common.create": "Erstellen",
                "common.search": "Suchen",
                "common.loading": "Laden...",
                "auth.login": "Anmelden",
                "auth.logout": "Abmelden",
                "auth.register": "Registrieren",
                "auth.email": "E-Mail",
                "auth.password": "Passwort",
                "error.not_found": "Ressource nicht gefunden",
                "error.unauthorized": "Unbefugt",
            },
        )

    def set_locale(self, locale: str) -> None:
        if locale in self.SUPPORTED_LOCALES:
            self._current_locale = locale
        else:
            logger.warning("Unsupported locale: %s", locale)

    def set_fallback_locale(self, locale: str) -> None:
        self._fallback_locale = locale

    def t(self, key: str, locale: str | None = None, **kwargs: Any) -> str:
        target_locale = locale or self._current_locale
        translations = self._translations.get(target_locale)
        if translations and key in translations.translations:
            result = translations.translations[key]
        else:
            fallback = self._translations.get(self._fallback_locale)
            if fallback and key in fallback.translations:
                result = fallback.translations[key]
            else:
                result = key

        for k, v in kwargs.items():
            result = result.replace(f"{{{{{k}}}}}", str(v))
        return result

    def load_translations(self, locale: str, file_path: str) -> bool:
        try:
            path = Path(file_path)
            if not path.exists():
                return False
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self._translations[locale] = TranslationSet(
                locale=locale,
                translations=data,
            )
            return True
        except Exception as e:
            logger.error("Failed to load translations for %s: %s", locale, e)
            return False

    def export_translations(self, locale: str) -> dict[str, str] | None:
        ts = self._translations.get(locale)
        return dict(ts.translations) if ts else None

    def get_supported_locales(self) -> list[str]:
        return list(self._translations.keys())

    def get_missing_keys(self, locale: str) -> list[str]:
        base = self._translations.get(self._fallback_locale)
        target = self._translations.get(locale)
        if not base:
            return []
        if not target:
            return list(base.translations.keys())
        return [k for k in base.translations if k not in target.translations]

    def get_stats(self) -> dict[str, Any]:
        return {
            "current_locale": self._current_locale,
            "fallback_locale": self._fallback_locale,
            "supported_locales": self.get_supported_locales(),
            "translation_counts": {
                locale: len(ts.translations)
                for locale, ts in self._translations.items()
            },
        }


i18n = I18nService()
