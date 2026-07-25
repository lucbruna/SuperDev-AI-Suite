const vscode = require("vscode");

function activate(context) {
  context.subscriptions.push(
    vscode.commands.registerCommand("superdev.openDashboard", () => {
      vscode.env.openExternal(vscode.Uri.parse("http://localhost:3000/dashboard"));
    })
  );
  context.subscriptions.push(
    vscode.commands.registerCommand("superdev.runWorkflow", async () => {
      const workflow = await vscode.window.showInputBox({ prompt: "Workflow ID" });
      if (workflow) {
        vscode.window.showInformationMessage(`Running workflow: ${workflow}`);
      }
    })
  );
}

function deactivate() {}

module.exports = { activate, deactivate };
