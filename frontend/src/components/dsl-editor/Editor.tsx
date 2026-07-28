"use client";

import { useState } from "react";
import Editor, { OnMount } from "@monaco-editor/react";
import { Preview } from "./Preview";
import { Validator } from "./Validator";

const DEFAULT_YAML = `# SuperDev Workflow DSL
name: my-workflow
version: "1.0"
steps:
  - type: agent
    agent: Architect
    prompt: "Design the system architecture"
    model: gpt-4o

  - type: code
    language: python
    command: "pytest tests/"

  - type: deploy
    environment: staging
    strategy: blue-green
`;

export function DSLEditor() {
  const [yaml, setYaml] = useState(DEFAULT_YAML);
  const [errors, setErrors] = useState<string[]>([]);

  const handleEditorMount: OnMount = (editor, monaco) => {
    monaco.languages.registerCompletionItemProvider("yaml", {
      provideCompletionItems: (model, position) => {
        const word = model.getWordUntilPosition(position);
        const range = {
          startLineNumber: position.lineNumber,
          endLineNumber: position.lineNumber,
          startColumn: word.startColumn,
          endColumn: word.endColumn,
        };
        const suggestions = [
          { label: "type", insertText: "type: ", kind: monaco.languages.CompletionItemKind.Keyword, range },
          { label: "agent", insertText: "agent: ", kind: monaco.languages.CompletionItemKind.Keyword, range },
          { label: "prompt", insertText: "prompt: ", kind: monaco.languages.CompletionItemKind.Keyword, range },
          { label: "model", insertText: "model: ", kind: monaco.languages.CompletionItemKind.Keyword, range },
          { label: "environment", insertText: "environment: ", kind: monaco.languages.CompletionItemKind.Keyword, range },
          { label: "strategy", insertText: "strategy: ", kind: monaco.languages.CompletionItemKind.Keyword, range },
          { label: "language", insertText: "language: ", kind: monaco.languages.CompletionItemKind.Keyword, range },
          { label: "command", insertText: "command: ", kind: monaco.languages.CompletionItemKind.Keyword, range },
        ];
        return { suggestions };
      },
    });
  };

  const validate = () => {
    const errs: string[] = [];
    try {
      const parsed = parseYamlSimple(yaml);
      if (!parsed.name) errs.push("Missing 'name' field");
      if (!parsed.steps || !Array.isArray(parsed.steps)) errs.push("Missing or invalid 'steps' array");
      if (parsed.steps) {
        parsed.steps.forEach((step: any, i: number) => {
          if (!step.type) errs.push(`Step ${i + 1}: missing 'type'`);
        });
      }
    } catch {
      errs.push("Invalid YAML syntax");
    }
    setErrors(errs);
  };

  return (
    <div className="grid grid-cols-2 gap-4">
      <div className="rounded-xl border dark:border-surface-700 overflow-hidden">
        <div className="flex items-center justify-between border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
          <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">DSL Editor</span>
          <button onClick={validate} className="rounded bg-primary-600 px-3 py-1 text-xs text-white hover:bg-primary-700">Validate</button>
        </div>
        <Editor
          height="500px"
          defaultLanguage="yaml"
          value={yaml}
          onChange={(val) => setYaml(val || "")}
          onMount={handleEditorMount}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 13,
            lineNumbers: "on",
            renderWhitespace: "selection",
            tabSize: 2,
          }}
        />
      </div>
      <div className="space-y-4">
        <Preview yaml={yaml} />
        <Validator errors={errors} onFix={() => setYaml(DEFAULT_YAML)} />
      </div>
    </div>
  );
}

function parseYamlSimple(text: string): any {
  const lines = text.split("\n");
  const result: any = {};
  let currentKey: string | null = null;
  let currentArray: any[] = [];
  let inArray = false;

  for (const line of lines) {
    if (!line.trim() || line.trim().startsWith("#")) continue;
    const indent = line.search(/\S/);
    const [key, ...rest] = line.trim().split(":");
    const value = rest.join(":").trim();

    if (indent === 0) {
      if (inArray) {
        result[currentKey!] = currentArray;
        currentArray = [];
        inArray = false;
      }
      currentKey = key;
      if (value === "") {
        inArray = key === "steps";
        result[currentKey] = inArray ? [] : {};
      } else {
        result[currentKey] = value;
      }
    } else if (indent === 2) {
      if (inArray && currentArray.length > 0) {
        const obj = currentArray[currentArray.length - 1];
        if (typeof obj === "object") obj[key] = value;
      }
    } else if (indent === 0 && key === "-") {
      currentArray.push({});
    }
  }
  if (inArray) result[currentKey!] = currentArray;
  return result;
}