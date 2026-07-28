import * as vscode from 'vscode';

export class WorkflowTreeProvider implements vscode.TreeDataProvider<WorkflowItem> {
  private _onDidChangeTreeData: vscode.EventEmitter<WorkflowItem | undefined | null> = new vscode.EventEmitter();
  readonly onDidChangeTreeData: vscode.Event<WorkflowItem | undefined | null> = this._onDidChangeTreeData.event;

  private workflows: WorkflowItem[] = [
    new WorkflowItem('CI/CD Pipeline', 'running', 'wf_001', [
      new WorkflowItem('Build', 'completed', 'wf_001_build'),
      new WorkflowItem('Test', 'running', 'wf_001_test'),
      new WorkflowItem('Deploy', 'pending', 'wf_001_deploy'),
    ]),
    new WorkflowItem('Code Review', 'idle', 'wf_002'),
    new WorkflowItem('Data Pipeline', 'failed', 'wf_003', [
      new WorkflowItem('Extract', 'completed', 'wf_003_extract'),
      new WorkflowItem('Transform', 'error', 'wf_003_transform'),
    ]),
  ];

  refresh(): void {
    this._onDidChangeTreeData.fire(null);
  }

  getTreeItem(element: WorkflowItem): vscode.TreeItem {
    return element;
  }

  getChildren(element?: WorkflowItem): Thenable<WorkflowItem[]> {
    if (element) return Promise.resolve(element.children || []);
    return Promise.resolve(this.workflows);
  }
}

class WorkflowItem extends vscode.TreeItem {
  constructor(
    public readonly label: string,
    public readonly status: string,
    public readonly id: string,
    public readonly children?: WorkflowItem[]
  ) {
    super(label, children ? vscode.TreeItemCollapsibleState.Collapsed : vscode.TreeItemCollapsibleState.None);
    this.tooltip = `${this.label} (${this.status})`;
    this.description = this.status;
    this.iconPath = this._icon();
    this.command = {
      command: 'superdev.runWorkflow',
      title: 'Run Workflow',
      arguments: [this.id],
    };
    this.contextValue = 'workflow';
  }

  private _icon(): vscode.ThemeIcon {
    const icons: Record<string, vscode.ThemeIcon> = {
      running: new vscode.ThemeIcon('play', new vscode.ThemeColor('debugIcon.startForeground')),
      completed: new vscode.ThemeIcon('pass', new vscode.ThemeColor('testing.iconPassed')),
      failed: new vscode.ThemeIcon('error', new vscode.ThemeColor('testing.iconFailed')),
      error: new vscode.ThemeIcon('error', new vscode.ThemeColor('testing.iconFailed')),
      pending: new vscode.ThemeIcon('circle-outline'),
      idle: new vscode.ThemeIcon('circle-outline'),
    };
    return icons[this.status] || new vscode.ThemeIcon('circle-outline');
  }
}