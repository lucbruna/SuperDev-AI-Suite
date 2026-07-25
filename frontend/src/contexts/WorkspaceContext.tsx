"use client";

import {
  createContext,
  useCallback,
  useMemo,
  useReducer,
  type ReactNode,
} from "react";

interface FileNode {
  id: string;
  name: string;
  path: string;
  type: "file" | "folder";
  children?: FileNode[];
  language?: string;
  size?: number;
}

interface WorkspaceState {
  projectId: string | null;
  projectName: string | null;
  files: FileNode[];
  selectedFilePath: string | null;
  isSidebarOpen: boolean;
  sidebarWidth: number;
}

type WorkspaceAction =
  | { type: "SET_PROJECT"; payload: { id: string; name: string } }
  | { type: "SET_FILES"; payload: FileNode[] }
  | { type: "SELECT_FILE"; payload: string }
  | { type: "TOGGLE_SIDEBAR" }
  | { type: "SET_SIDEBAR_WIDTH"; payload: number }
  | { type: "RESET" };

const initialState: WorkspaceState = {
  projectId: null,
  projectName: null,
  files: [],
  selectedFilePath: null,
  isSidebarOpen: true,
  sidebarWidth: 280,
};

function workspaceReducer(state: WorkspaceState, action: WorkspaceAction): WorkspaceState {
  switch (action.type) {
    case "SET_PROJECT":
      return {
        ...state,
        projectId: action.payload.id,
        projectName: action.payload.name,
      };
    case "SET_FILES":
      return { ...state, files: action.payload };
    case "SELECT_FILE":
      return { ...state, selectedFilePath: action.payload };
    case "TOGGLE_SIDEBAR":
      return { ...state, isSidebarOpen: !state.isSidebarOpen };
    case "SET_SIDEBAR_WIDTH":
      return { ...state, sidebarWidth: action.payload };
    case "RESET":
      return initialState;
    default:
      return state;
  }
}

interface WorkspaceContextValue {
  state: WorkspaceState;
  setProject: (id: string, name: string) => void;
  setFiles: (files: FileNode[]) => void;
  selectFile: (path: string) => void;
  toggleSidebar: () => void;
  setSidebarWidth: (width: number) => void;
  reset: () => void;
}

export const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

interface WorkspaceProviderProps {
  children: ReactNode;
}

export function WorkspaceProvider({ children }: WorkspaceProviderProps) {
  const [state, dispatch] = useReducer(workspaceReducer, initialState);

  const setProject = useCallback((id: string, name: string) => {
    dispatch({ type: "SET_PROJECT", payload: { id, name } });
  }, []);

  const setFiles = useCallback((files: FileNode[]) => {
    dispatch({ type: "SET_FILES", payload: files });
  }, []);

  const selectFile = useCallback((path: string) => {
    dispatch({ type: "SELECT_FILE", payload: path });
  }, []);

  const toggleSidebar = useCallback(() => {
    dispatch({ type: "TOGGLE_SIDEBAR" });
  }, []);

  const setSidebarWidth = useCallback((width: number) => {
    dispatch({ type: "SET_SIDEBAR_WIDTH", payload: width });
  }, []);

  const reset = useCallback(() => {
    dispatch({ type: "RESET" });
  }, []);

  const value = useMemo(
    () => ({
      state,
      setProject,
      setFiles,
      selectFile,
      toggleSidebar,
      setSidebarWidth,
      reset,
    }),
    [state, setProject, setFiles, selectFile, toggleSidebar, setSidebarWidth, reset],
  );

  return <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>;
}
