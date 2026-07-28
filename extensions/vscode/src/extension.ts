import * as vscode from 'vscode';
import { WorkflowTreeProvider } from './treeView';
import { SuperDevWebview } from './webview/panel';

let workflowTree: WorkflowTreeProvider;

export function activate(context: vscode.ExtensionContext) {
  workflowTree = new WorkflowTreeProvider();
  vscode.window.registerTreeDataProvider('superdev.workflows', workflowTree);

  const disposable = vscode.commands.registerCommand('superdev.openDashboard', () => {
    SuperDevWebview.createOrShow(context.extensionUri);
  });

  context.subscriptions.push(disposable);

  context.subscriptions.push(
    vscode.commands.registerCommand('superdev.runWorkflow', async (workflowId?: string) => {
      const id = workflowId || await vscode.window.showInputBox({ prompt: 'Workflow ID' });
      if (!id) return;
      vscode.window.withProgress({ location: vscode.ProgressLocation.Notification, title: `Running workflow ${id}` }, async () => {
        await new Promise(resolve => setTimeout(resolve, 2000));
        vscode.window.showInformationMessage(`Workflow ${id} completed`);
      });
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('superdev.refreshWorkflows', () => workflowTree.refresh())
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('superdev.viewAgentLogs', async (agentId: string) => {
      const panel = vscode.window.createOutputChannel(`Agent: ${agentId}`);
      panel.appendLine(`[SuperDev] Logs for agent ${agentId}`);
      panel.appendLine('[SuperDev] Connected. Waiting for events...');
      panel.show();
    })
  );

  vscode.languages.registerDocumentSemanticTokensProvider(
    { language: 'superdev-dsl', scheme: 'file' },
    new (class implements vscode.DocumentSemanticTokensProvider {
      provideDocumentSemanticTokens(document: vscode.TextDocument): vscode.SemanticTokens {
        const tokensBuilder = new vscode.SemanticTokensBuilder();
        for (let i = 0; i < document.lineCount; i++) {
          const line = document.lineAt(i);
          if (line.text.includes('agent:')) tokensBuilder.push(line.lineNumber, 0, 5, 1);
          if (line.text.includes('workflow:')) tokensBuilder.push(line.lineNumber, 0, 9, 2);
          if (line.text.includes('steps:')) tokensBuilder.push(line.lineNumber, 0, 6, 3);
        }
        return tokensBuilder.build();
      }
    })(),
    new vscode.SemanticTokensLegend(['keyword', 'type', 'function'])
  );

  vscode.window.showInformationMessage('SuperDev extension activated');
}

export function deactivate() {
  SuperDevWebview.currentPanel?.dispose();
}