"use client";

interface ErrorExplainerProps {
  errorText: string;
  onFix: (command: string) => void;
}

interface Explanation {
  problem: string;
  suggestion: string;
  command?: string;
}

function parseError(text: string): Explanation[] {
  const explanations: Explanation[] = [];

  if (text.includes("ModuleNotFoundError") || text.includes("ImportError")) {
    const match = text.match(/No module named ['\"](.+)['\"]/);
    const mod = match ? match[1] : "unknown";
    explanations.push({
      problem: `Missing Python module: ${mod}`,
      suggestion: `Install ${mod} with pip`,
      command: `pip install ${mod}`,
    });
  }

  if (text.includes("SyntaxError") || text.includes("unexpected token")) {
    explanations.push({
      problem: "Syntax error detected",
      suggestion: "Check for missing bracket, parenthesis, or semicolon near the indicated line",
    });
  }

  if (text.includes("ENOENT") || text.includes("No such file")) {
    const match = text.match(/ENOENT.*['\"](.+)['\"]/);
    const file = match ? match[1] : "file";
    explanations.push({
      problem: `File not found: ${file}`,
      suggestion: "Verify the file path and create it if needed",
      command: `touch ${file}`,
    });
  }

  if (text.includes("EACCES") || text.includes("Permission denied")) {
    explanations.push({
      problem: "Permission denied",
      suggestion: "Use elevated permissions or check file ownership",
    });
  }

  if (text.includes("ETIMEDOUT") || text.includes("Timeout")) {
    explanations.push({
      problem: "Network timeout",
      suggestion: "Check internet connection or increase timeout value",
    });
  }

  if (text.includes("ERR_MODULE_NOT_FOUND") || text.includes("Cannot find module")) {
    const match = text.match(/Cannot find module ['\"](.+)['\"]/);
    const mod = match ? match[1] : "unknown";
    explanations.push({
      problem: `Missing Node.js module: ${mod}`,
      suggestion: `Install ${mod} with npm`,
      command: `npm install ${mod}`,
    });
  }

  if (text.includes("TypeError") && text.includes("undefined")) {
    explanations.push({
      problem: "Attempted to access property of undefined",
      suggestion: "Check that the object exists before accessing its properties",
    });
  }

  if (explanations.length === 0) {
    explanations.push({
      problem: "Unrecognized error pattern",
      suggestion: "Try searching for a portion of this error on Stack Overflow or in the project docs",
    });
  }

  return explanations;
}

export function ErrorExplainer({ errorText, onFix }: ErrorExplainerProps) {
  if (!errorText.trim()) return null;

  const explanations = parseError(errorText);

  return (
    <div className="rounded-xl border border-red-800 bg-red-950/30 p-4">
      <h3 className="text-xs font-semibold text-red-400 uppercase">Error Analysis</h3>
      <div className="mt-2 space-y-3">
        {explanations.map((exp, i) => (
          <div key={i} className="rounded-lg bg-red-950/50 p-3">
            <p className="text-xs font-medium text-red-300">{exp.problem}</p>
            <p className="mt-1 text-xs text-gray-400">{exp.suggestion}</p>
            {exp.command && (
              <button
                onClick={() => onFix(exp.command!)}
                className="mt-2 rounded bg-red-800 px-2 py-1 text-xs text-red-200 hover:bg-red-700"
              >
                Run: {exp.command}
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}