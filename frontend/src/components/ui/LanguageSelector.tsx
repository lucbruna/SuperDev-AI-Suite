"use client";

import { useI18n } from "../../i18n";
import type { Locale } from "../../i18n/types";

const LOCALE_LABELS: Record<Locale, string> = {
  "pt-BR": "Português (Brasil)",
  en: "English",
  es: "Español",
};

export function LanguageSelector() {
  const { locale, setLocale, availableLocales } = useI18n();

  return (
    <select
      value={locale}
      onChange={(e) => setLocale(e.target.value as Locale)}
      className="px-3 py-2 border rounded-lg text-sm bg-white dark:bg-gray-800"
    >
      {availableLocales.map((loc) => (
        <option key={loc} value={loc}>
          {LOCALE_LABELS[loc]}
        </option>
      ))}
    </select>
  );
}
