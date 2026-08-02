import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/** Combina classes Tailwind com resolução de conflitos. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Formata número monetário em USD. */
export function formatUSD(value: number, digits = 2): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value || 0);
}

/** Formata data ISO para pt-BR relativo ou absoluto. */
export function formatDate(value: string | null | undefined): string {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '—';
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

/** Tempo relativo em pt-BR ("há 5 min"). */
export function timeAgo(value: string | null | undefined): string {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '—';
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
  const intervals: Array<[number, string]> = [
    [60, 'seg'],
    [3600, 'min'],
    [86400, 'h'],
    [604800, 'd'],
    [2592000, 'meses'],
  ];
  if (seconds < 60) return 'agora';
  let valueOut = seconds;
  let unit = 'seg';
  for (const [limit, label] of intervals) {
    if (seconds < limit) break;
    valueOut = Math.floor(seconds / (limit / (limit === 60 ? 1 : limit)));
    unit = label;
  }
  // Recalcula de forma simples para precisão
  if (seconds < 3600) {
    valueOut = Math.floor(seconds / 60);
    unit = 'min';
  } else if (seconds < 86400) {
    valueOut = Math.floor(seconds / 3600);
    unit = 'h';
  } else if (seconds < 604800) {
    valueOut = Math.floor(seconds / 86400);
    unit = 'd';
  } else {
    valueOut = Math.floor(seconds / 2592000);
    unit = valueOut > 1 ? 'meses' : 'mês';
  }
  return `há ${valueOut} ${unit}`;
}

/** Inicial maiúscula. */
export function capitalize(value: string): string {
  if (!value) return value;
  return value.charAt(0).toUpperCase() + value.slice(1);
}
