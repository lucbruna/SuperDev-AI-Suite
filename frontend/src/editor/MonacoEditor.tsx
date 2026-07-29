"use client";

import React, { useRef, useEffect, useState } from "react";
import { useEditorStore } from "@/stores/editorStore";

interface MonacoEditorProps {
  language?: string;
  value?: string;
  onChange?: (value: string) => void;
  readOnly?: boolean;
  className?: string;
}

export function MonacoEditor({
  language = "python",
  value = "",
  onChange,
  readOnly = false,
  className = "",
}: MonacoEditorProps) {
  const editorRef = useRef<HTMLDivElement>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const { fontSize, wordWrap, minimap, lineNumbers } = useEditorStore();

  useEffect(() => {
    if (!editorRef.current) return;

    const loadMonaco = async () => {
      if (typeof window !== "undefined" && (window as any).monaco) {
        setIsLoaded(true);
        return;
      }

      const script = document.createElement("script");
      script.src = "https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs/loader.js";
      script.onload = () => {
        (window as any).require.config({
          paths: { vs: "https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs" },
        });
        (window as any).require(["vs/editor/editor.main"], () => {
          setIsLoaded(true);
        });
      };
      document.head.appendChild(script);
    };

    loadMonaco();
  }, []);

  useEffect(() => {
    if (!isLoaded || !editorRef.current) return;

    const monaco = (window as any).monaco;
    const editor = monaco.editor.create(editorRef.current, {
      value,
      language,
      readOnly,
      fontSize,
      minimap: { enabled: minimap },
      wordWrap: wordWrap ? "on" : "off",
      lineNumbers: lineNumbers ? "on" : "off",
      scrollBeyondLastLine: false,
      automaticLayout: true,
      theme: "vs-dark",
    });

    editor.onDidChangeModelContent(() => {
      onChange?.(editor.getValue());
    });

    return () => editor.dispose();
  }, [isLoaded, language, readOnly, fontSize, wordWrap, minimap, lineNumbers, value, onChange]);

  return (
    <div className={`relative ${className}`}>
      {!isLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-muted/50">
          <span className="text-sm text-muted-foreground">Loading editor...</span>
        </div>
      )}
      <div ref={editorRef} className="w-full h-full min-h-[400px]" />
    </div>
  );
}
