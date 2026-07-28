"use client";

import { useState, useCallback } from "react";

interface DiffFile {
  path: string;
  status: "added" | "modified" | "deleted";
  content: string;
}

export function useDiffMerge() {
  const [files, setFiles] = useState<DiffFile[]>([]);
  const [accepted, setAccepted] = useState<Set<string>>(new Set());
  const [rejected, setRejected] = useState<Set<string>>(new Set());

  const loadDiff = useCallback((diffFiles: DiffFile[]) => {
    setFiles(diffFiles);
    setAccepted(new Set());
    setRejected(new Set());
  }, []);

  const acceptFile = useCallback((path: string) => {
    setAccepted((prev) => new Set([...prev, path]));
    setRejected((prev) => { const next = new Set(prev); next.delete(path); return next; });
  }, []);

  const rejectFile = useCallback((path: string) => {
    setRejected((prev) => new Set([...prev, path]));
    setAccepted((prev) => { const next = new Set(prev); next.delete(path); return next; });
  }, []);

  const acceptAll = useCallback(() => {
    setAccepted(new Set(files.map((f) => f.path)));
    setRejected(new Set());
  }, [files]);

  const rejectAll = useCallback(() => {
    setRejected(new Set(files.map((f) => f.path)));
    setAccepted(new Set());
  }, [files]);

  const applySelected = useCallback(async () => {
    const toApply = files.filter((f) => accepted.has(f.path));
    for (const file of toApply) {
      await fetch(`/api/v1/workspace/diff/apply`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: file.path, content: file.content }),
      });
    }
    return toApply.map((f) => f.path);
  }, [files, accepted]);

  const hasChanges = files.length > 0;
  const acceptedCount = accepted.size;
  const rejectedCount = rejected.size;
  const totalCount = files.length;

  return {
    files, accepted, rejected, loadDiff,
    acceptFile, rejectFile, acceptAll, rejectAll, applySelected,
    hasChanges, acceptedCount, rejectedCount, totalCount,
  };
}