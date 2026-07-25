"use client";

import { createContext, useContext, useState, useCallback, type ReactNode } from "react";
import type { Locale, TranslationKeys } from "./types";
import { translations } from "./translations";

interface I18nContextValue {
  locale: Locale;
  t: TranslationKeys;
  setLocale: (locale: Locale) => void;
  availableLocales: Locale[];
}

const I18nContext = createContext<I18nContextValue | null>(null);

const AVAILABLE_LOCALES: Locale[] = ["pt-BR", "en", "es"];

function getInitialLocale(): Locale {
  if (typeof window !== "undefined") {
    const saved = localStorage.getItem("superdev-locale") as Locale;
    if (saved && AVAILABLE_LOCALES.includes(saved)) return saved;

    const browserLang = navigator.language;
    if (browserLang.startsWith("pt")) return "pt-BR";
    if (browserLang.startsWith("es")) return "es";
  }
  return "en";
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(getInitialLocale);

  const setLocale = useCallback((newLocale: Locale) => {
    setLocaleState(newLocale);
    localStorage.setItem("superdev-locale", newLocale);
    document.documentElement.lang = newLocale;
  }, []);

  const value: I18nContextValue = {
    locale,
    t: translations[locale],
    setLocale,
    availableLocales: AVAILABLE_LOCALES,
  };

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nContextValue {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error("useI18n must be used within an I18nProvider");
  }
  return context;
}
