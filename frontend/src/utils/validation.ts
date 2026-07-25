export const validators = {
  required: (value: string): string | undefined => {
    if (!value || value.trim().length === 0) {
      return "This field is required";
    }
    return undefined;
  },

  email: (value: string): string | undefined => {
    if (!value) return undefined;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      return "Invalid email address";
    }
    return undefined;
  },

  password: (value: string): string | undefined => {
    if (!value) return undefined;
    if (value.length < 8) {
      return "Password must be at least 8 characters";
    }
    if (!/[A-Z]/.test(value)) {
      return "Password must contain an uppercase letter";
    }
    if (!/[a-z]/.test(value)) {
      return "Password must contain a lowercase letter";
    }
    if (!/[0-9]/.test(value)) {
      return "Password must contain a number";
    }
    return undefined;
  },

  username: (value: string): string | undefined => {
    if (!value) return undefined;
    if (value.length < 3) {
      return "Username must be at least 3 characters";
    }
    if (value.length > 30) {
      return "Username must be at most 30 characters";
    }
    if (!/^[a-zA-Z0-9_]+$/.test(value)) {
      return "Username can only contain letters, numbers, and underscores";
    }
    return undefined;
  },

  url: (value: string): string | undefined => {
    if (!value) return undefined;
    try {
      new URL(value);
      return undefined;
    } catch {
      return "Invalid URL";
    }
  },

  minLength: (min: number) => (value: string): string | undefined => {
    if (value && value.length < min) {
      return `Must be at least ${min} characters`;
    }
    return undefined;
  },

  maxLength: (max: number) => (value: string): string | undefined => {
    if (value && value.length > max) {
      return `Must be at most ${max} characters`;
    }
    return undefined;
  },

  match: (otherValue: string, fieldName: string) => (value: string): string | undefined => {
    if (value !== otherValue) {
      return `Must match ${fieldName}`;
    }
    return undefined;
  },
};

export function validate<T extends Record<string, string>>(
  values: T,
  rules: Record<keyof T, ((value: string) => string | undefined)[]>,
): Partial<Record<keyof T, string>> {
  const errors: Partial<Record<keyof T, string>> = {};

  for (const field in rules) {
    for (const rule of rules[field]) {
      const error = rule(values[field]);
      if (error) {
        errors[field] = error;
        break;
      }
    }
  }

  return errors;
}
