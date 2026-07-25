const PREFIX = "superdev_";

export const storage = {
  get<T>(key: string): T | null {
    try {
      const item = localStorage.getItem(PREFIX + key);
      return item ? (JSON.parse(item) as T) : null;
    } catch {
      return null;
    }
  },

  set<T>(key: string, value: T): void {
    try {
      localStorage.setItem(PREFIX + key, JSON.stringify(value));
    } catch {
      console.warn("Failed to save to localStorage:", key);
    }
  },

  remove(key: string): void {
    try {
      localStorage.removeItem(PREFIX + key);
    } catch {
      console.warn("Failed to remove from localStorage:", key);
    }
  },

  clear(): void {
    try {
      const keys = Object.keys(localStorage).filter((k) => k.startsWith(PREFIX));
      keys.forEach((k) => localStorage.removeItem(k));
    } catch {
      console.warn("Failed to clear localStorage");
    }
  },
};

export default storage;
