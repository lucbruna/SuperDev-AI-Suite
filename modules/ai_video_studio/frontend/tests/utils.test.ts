import { describe, expect, it } from 'vitest';
import { formatBytes, formatDuration, formatNumber, timeAgo } from '../src/utils';

describe('formatBytes', () => {
  it('formats zero and negatives as 0 B', () => {
    expect(formatBytes(0)).toBe('0 B');
    expect(formatBytes(-5)).toBe('0 B');
  });

  it('formats non-finite values as 0 B', () => {
    expect(formatBytes(Number.NaN)).toBe('0 B');
    expect(formatBytes(Number.POSITIVE_INFINITY)).toBe('0 B');
  });

  it('formats plain bytes without decimals', () => {
    expect(formatBytes(512)).toBe('512 B');
  });

  it('formats KB, MB and GB', () => {
    expect(formatBytes(1024)).toBe('1.0 KB');
    expect(formatBytes(5 * 1024 * 1024)).toBe('5.0 MB');
    expect(formatBytes(1.5 * 1024 * 1024 * 1024)).toBe('1.5 GB');
  });
});

describe('formatNumber', () => {
  it('formats small numbers plainly', () => {
    expect(formatNumber(0)).toBe('0');
    expect(formatNumber(500)).toBe('500');
    expect(formatNumber(-42)).toBe('-42');
  });

  it('formats thousands with K', () => {
    expect(formatNumber(1500)).toBe('1.5K');
    expect(formatNumber(12000)).toBe('12.0K');
  });

  it('formats millions with M', () => {
    expect(formatNumber(2_500_000)).toBe('2.5M');
  });

  it('handles non-finite values', () => {
    expect(formatNumber(Number.NaN)).toBe('0');
    expect(formatNumber(Number.POSITIVE_INFINITY)).toBe('0');
  });
});

describe('formatDuration', () => {
  it('formats under a minute', () => {
    expect(formatDuration(0)).toBe('00:00');
    expect(formatDuration(59)).toBe('00:59');
  });

  it('formats minutes', () => {
    expect(formatDuration(65)).toBe('01:05');
    expect(formatDuration(600)).toBe('10:00');
  });

  it('formats hours', () => {
    expect(formatDuration(3600)).toBe('1:00:00');
    expect(formatDuration(3661)).toBe('1:01:01');
  });

  it('handles negatives and non-finite', () => {
    expect(formatDuration(-5)).toBe('00:00');
    expect(formatDuration(Number.NaN)).toBe('00:00');
  });
});

describe('timeAgo', () => {
  const now = Date.now();

  it('returns just now for recent timestamps', () => {
    expect(timeAgo(new Date(now - 5_000).toISOString())).toBe('just now');
  });

  it('returns minutes ago', () => {
    expect(timeAgo(new Date(now - 5 * 60_000).toISOString())).toBe('5m ago');
  });

  it('returns hours ago', () => {
    expect(timeAgo(new Date(now - 3 * 3_600_000).toISOString())).toBe('3h ago');
  });

  it('returns days ago', () => {
    expect(timeAgo(new Date(now - 2 * 86_400_000).toISOString())).toBe('2d ago');
  });

  it('returns months ago', () => {
    expect(timeAgo(new Date(now - 45 * 86_400_000).toISOString())).toBe('1mo ago');
  });

  it('returns years ago', () => {
    expect(timeAgo(new Date(now - 2 * 365 * 86_400_000).toISOString())).toBe('2y ago');
  });

  it('falls back to recently for invalid dates', () => {
    expect(timeAgo('not-a-date')).toBe('recently');
  });
});
