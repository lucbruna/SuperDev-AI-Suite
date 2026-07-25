"use client";

import { useContext, useCallback } from "react";
import { WorkspaceContext } from "@/contexts/WorkspaceContext";
import type { WorkspaceFile } from "@/types/workspace";

export function useWorkspace() {
  const context = useContext(WorkspaceContext);
  if (!context) {
    throw new Error("useWorkspace must be used within a WorkspaceProvider");
  }

  const { state, setProject, setFiles, selectFile, toggleSidebar, setSidebarWidth, reset } = context;

  const openFile = useCallback(
    (path: string) => {
      selectFile(path);
    },
    [selectFile],
  );

  const saveFile = useCallback(
    async (_path: string, _content: string) => {
      // Implemented by the editor store / API integration
    },
    [],
  );

  const createFile = useCallback(
    (_name: string, _type: "file" | "folder", _parentPath?: string) => {
      // Implemented by the API
    },
    [],
  );

  const deleteFile = useCallback(
    (_path: string) => {
      // Implemented by the API
    },
    [],
  );

  return {
    workspace: state.projectId
      ? { id: state.projectId, name: state.projectName ?? "", files: state.files as WorkspaceFile[] }
      : null,
    files: state.files as WorkspaceFile[],
    selectedFilePath: state.selectedFilePath,
    isSidebarOpen: state.isSidebarOpen,
    sidebarWidth: state.sidebarWidth,
    openFile,
    saveFile,
    createFile,
    deleteFile,
    setProject,
    setFiles,
    toggleSidebar,
    setSidebarWidth,
    reset,
  };
}
