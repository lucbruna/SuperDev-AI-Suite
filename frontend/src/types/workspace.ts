export interface Workspace {
  id: string;
  project_id: string;
  name: string;
  files: WorkspaceFile[];
  created_at: string;
  updated_at: string;
}

export interface WorkspaceFile {
  name: string;
  path: string;
  type: "file" | "folder";
  size?: number;
  modified?: string;
  children?: WorkspaceFile[];
}

export interface FileTree {
  root: WorkspaceFile;
  flat: WorkspaceFile[];
  depth: number;
}
