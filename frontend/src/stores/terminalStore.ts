import { create } from "zustand";
import { devtools } from "zustand/middleware";

interface TerminalSession {
  id: string;
  name: string;
  command: string;
  output: string[];
  isRunning: boolean;
  cwd: string;
}

interface TerminalStore {
  sessions: TerminalSession[];
  activeSessionId: string | null;
  isVisible: boolean;
  fontSize: number;
  createSession: (name?: string) => void;
  closeSession: (id: string) => void;
  setActiveSession: (id: string) => void;
  appendOutput: (sessionId: string, output: string) => void;
  setCommand: (sessionId: string, command: string) => void;
  setRunning: (sessionId: string, isRunning: boolean) => void;
  clearOutput: (sessionId: string) => void;
  toggleVisibility: () => void;
  setFontSize: (size: number) => void;
  clearAllSessions: () => void;
}

let sessionCounter = 0;

export const useTerminalStore = create<TerminalStore>()(
  devtools(
    (set) => ({
      sessions: [],
      activeSessionId: null,
      isVisible: true,
      fontSize: 13,

      createSession: (name) =>
        set((state) => {
          const id = `term-${++sessionCounter}`;
          const session: TerminalSession = {
            id,
            name: name ?? `Terminal ${sessionCounter}`,
            command: "",
            output: [],
            isRunning: false,
            cwd: "/",
          };
          return {
            sessions: [...state.sessions, session],
            activeSessionId: id,
          };
        }),

      closeSession: (id) =>
        set((state) => {
          const sessions = state.sessions.filter((s) => s.id !== id);
          const activeSessionId =
            state.activeSessionId === id
              ? sessions[sessions.length - 1]?.id ?? null
              : state.activeSessionId;
          return { sessions, activeSessionId };
        }),

      setActiveSession: (activeSessionId) => set({ activeSessionId }),

      appendOutput: (sessionId, output) =>
        set((state) => ({
          sessions: state.sessions.map((s) =>
            s.id === sessionId
              ? { ...s, output: [...s.output, output] }
              : s,
          ),
        })),

      setCommand: (sessionId, command) =>
        set((state) => ({
          sessions: state.sessions.map((s) =>
            s.id === sessionId ? { ...s, command } : s,
          ),
        })),

      setRunning: (sessionId, isRunning) =>
        set((state) => ({
          sessions: state.sessions.map((s) =>
            s.id === sessionId ? { ...s, isRunning } : s,
          ),
        })),

      clearOutput: (sessionId) =>
        set((state) => ({
          sessions: state.sessions.map((s) =>
            s.id === sessionId ? { ...s, output: [] } : s,
          ),
        })),

      toggleVisibility: () =>
        set((state) => ({ isVisible: !state.isVisible })),

      setFontSize: (fontSize) => set({ fontSize }),

      clearAllSessions: () => set({ sessions: [], activeSessionId: null }),
    }),
  ),
);
