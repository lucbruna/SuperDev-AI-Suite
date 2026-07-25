import { create } from "zustand";
import { devtools } from "zustand/middleware";

interface EditorTab {
  id: string;
  name: string;
  path: string;
  language: string;
  isDirty: boolean;
  content: string;
}

interface EditorStore {
  tabs: EditorTab[];
  activeTabId: string | null;
  fontSize: number;
  wordWrap: boolean;
  minimap: boolean;
  lineNumbers: boolean;
  setActiveTab: (tabId: string) => void;
  openTab: (tab: EditorTab) => void;
  closeTab: (tabId: string) => void;
  updateTabContent: (tabId: string, content: string) => void;
  markTabClean: (tabId: string) => void;
  setFontSize: (size: number) => void;
  toggleWordWrap: () => void;
  toggleMinimap: () => void;
  toggleLineNumbers: () => void;
  closeAllTabs: () => void;
}

export const useEditorStore = create<EditorStore>()(
  devtools(
    (set) => ({
      tabs: [],
      activeTabId: null,
      fontSize: 14,
      wordWrap: true,
      minimap: true,
      lineNumbers: true,

      setActiveTab: (tabId) => set({ activeTabId: tabId }),

      openTab: (tab) =>
        set((state) => {
          const existing = state.tabs.find((t) => t.id === tab.id);
          if (existing) {
            return { activeTabId: tab.id };
          }
          return {
            tabs: [...state.tabs, tab],
            activeTabId: tab.id,
          };
        }),

      closeTab: (tabId) =>
        set((state) => {
          const tabs = state.tabs.filter((t) => t.id !== tabId);
          let activeTabId = state.activeTabId;
          if (activeTabId === tabId) {
            const idx = state.tabs.findIndex((t) => t.id === tabId);
            activeTabId = tabs[Math.min(idx, tabs.length - 1)]?.id ?? null;
          }
          return { tabs, activeTabId };
        }),

      updateTabContent: (tabId, content) =>
        set((state) => ({
          tabs: state.tabs.map((t) =>
            t.id === tabId ? { ...t, content, isDirty: true } : t,
          ),
        })),

      markTabClean: (tabId) =>
        set((state) => ({
          tabs: state.tabs.map((t) =>
            t.id === tabId ? { ...t, isDirty: false } : t,
          ),
        })),

      setFontSize: (fontSize) => set({ fontSize }),

      toggleWordWrap: () => set((state) => ({ wordWrap: !state.wordWrap })),

      toggleMinimap: () => set((state) => ({ minimap: !state.minimap })),

      toggleLineNumbers: () => set((state) => ({ lineNumbers: !state.lineNumbers })),

      closeAllTabs: () => set({ tabs: [], activeTabId: null }),
    }),
  ),
);
