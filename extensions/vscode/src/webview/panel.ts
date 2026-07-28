import * as vscode from 'vscode';

export class SuperDevWebview {
  public static currentPanel: SuperDevWebview | undefined;
  private _panel: vscode.WebviewPanel;
  private _extensionUri: vscode.Uri;

  private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
    this._panel = panel;
    this._extensionUri = extensionUri;
    this._panel.webview.html = this._getHtml();
  }

  public static createOrShow(extensionUri: vscode.Uri) {
    if (SuperDevWebview.currentPanel) {
      SuperDevWebview.currentPanel._panel.reveal(vscode.ViewColumn.Beside);
      return;
    }
    const panel = vscode.window.createWebviewPanel('superdev', 'SuperDev Dashboard', vscode.ViewColumn.Beside, {
      enableScripts: true,
      retainContextWhenHidden: true,
    });
    SuperDevWebview.currentPanel = new SuperDevWebview(panel, extensionUri);
    panel.onDidDispose(() => { SuperDevWebview.currentPanel = undefined; });
  }

  public dispose() { this._panel.dispose(); }

  private _getHtml(): string {
    return `<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>SuperDev</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 16px; background: var(--vscode-editor-background); color: var(--vscode-editor-foreground); }
  .header { display: flex; align-items: center; gap: 8px; margin-bottom: 20px; }
  .logo { font-size: 24px; font-weight: bold; color: var(--vscode-textLink-foreground); }
  .card { background: var(--vscode-editor-inactiveSelectionBackground); border-radius: 8px; padding: 12px; margin-bottom: 8px; cursor: pointer; }
  .card:hover { background: var(--vscode-list-hoverBackground); }
  .status { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
  .running { background: #4caf50; animation: pulse 1.5s infinite; }
  .pending { background: #ff9800; }
  .completed { background: #2196f3; }
  .failed { background: #f44336; }
  @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
  .actions { margin-top: 16px; display: flex; gap: 8px; }
  button { background: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; }
  button:hover { background: var(--vscode-button-hoverBackground); }
</style></head>
<body>
  <div class="header"><span class="logo">SuperDev</span><span style="color: var(--vscode-descriptionForeground);">AI Suite</span></div>
  <h3>Workflows</h3>
  <div class="card" onclick="run('wf_001')"><span class="status running"></span>CI/CD Pipeline <span style="float:right;color:var(--vscode-descriptionForeground);">running</span></div>
  <div class="card" onclick="run('wf_002')"><span class="status pending"></span>Code Review <span style="float:right;color:var(--vscode-descriptionForeground);">idle</span></div>
  <div class="card" onclick="run('wf_003')"><span class="status failed"></span>Data Pipeline <span style="float:right;color:var(--vscode-descriptionForeground);">failed</span></div>
  <div class="actions"><button onclick="openExternal()">Open Dashboard</button><button onclick="refresh()">Refresh</button></div>
  <script>
    const vscode = acquireVsCodeApi();
    function run(id) { vscode.postMessage({ command: 'runWorkflow', workflowId: id }); }
    function openExternal() { vscode.postMessage({ command: 'openExternal' }); }
    function refresh() { vscode.postMessage({ command: 'refresh' }); }
  </script>
</body></html>`;
  }
}