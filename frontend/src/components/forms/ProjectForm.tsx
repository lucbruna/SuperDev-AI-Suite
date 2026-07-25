"use client";

import { useState, type FormEvent } from "react";
import { Input } from "@/components/inputs/Input";
import { Select } from "@/components/inputs/Select";
import { FormField } from "@/components/forms/FormField";
import { Button } from "@/components/buttons/Button";
import { Badge } from "@/components/badges/Badge";
import { X } from "lucide-react";

const LANGUAGES = [
  { value: "typescript", label: "TypeScript" },
  { value: "javascript", label: "JavaScript" },
  { value: "python", label: "Python" },
  { value: "rust", label: "Rust" },
  { value: "go", label: "Go" },
  { value: "java", label: "Java" },
  { value: "csharp", label: "C#" },
  { value: "ruby", label: "Ruby" },
  { value: "cpp", label: "C++" },
];

const TEMPLATES = [
  { value: "", label: "None (empty project)" },
  { value: "nextjs", label: "Next.js App" },
  { value: "react", label: "React App" },
  { value: "node-api", label: "Node.js API" },
  { value: "python-fastapi", label: "Python FastAPI" },
  { value: "rust-cli", label: "Rust CLI" },
];

interface ProjectFormData {
  name: string;
  description: string;
  template: string;
  language: string;
  tags: string[];
}

interface ProjectFormProps {
  initialData?: Partial<ProjectFormData>;
  onSubmit: (data: ProjectFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function ProjectForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading,
}: ProjectFormProps) {
  const [name, setName] = useState(initialData?.name ?? "");
  const [description, setDescription] = useState(initialData?.description ?? "");
  const [template, setTemplate] = useState(initialData?.template ?? "");
  const [language, setLanguage] = useState(initialData?.language ?? "typescript");
  const [tags, setTags] = useState<string[]>(initialData?.tags ?? []);
  const [tagInput, setTagInput] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const addTag = () => {
    const trimmed = tagInput.trim();
    if (trimmed && !tags.includes(trimmed)) {
      setTags([...tags, trimmed]);
      setTagInput("");
    }
  };

  const removeTag = (tag: string) => {
    setTags(tags.filter((t) => t !== tag));
  };

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    if (!name.trim()) errs.name = "Project name is required";
    if (!language) errs.language = "Language is required";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    onSubmit({ name: name.trim(), description: description.trim(), template, language, tags });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <Input
        label="Project Name"
        placeholder="my-awesome-project"
        value={name}
        onChange={(e) => setName(e.target.value)}
        error={errors.name}
        autoFocus
      />

      <FormField label="Description">
        <textarea
          className="flex min-h-[80px] w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-sm text-surface-900 placeholder:text-surface-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-0 dark:bg-surface-900 dark:text-surface-100 dark:border-surface-600 dark:focus:ring-primary-400"
          placeholder="A short description of your project"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </FormField>

      <Select
        label="Template"
        options={TEMPLATES}
        placeholder="Select a template"
        value={template}
        onChange={(e) => setTemplate(e.target.value)}
      />

      <Select
        label="Language"
        options={LANGUAGES}
        placeholder="Select language"
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        error={errors.language}
      />

      <FormField label="Tags">
        <div className="flex gap-2">
          <Input
            placeholder="Add a tag"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                addTag();
              }
            }}
            containerClassName="flex-1"
          />
          <Button type="button" variant="secondary" size="sm" onClick={addTag}>
            Add
          </Button>
        </div>
        {tags.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1.5">
            {tags.map((tag) => (
              <Badge key={tag} variant="default" size="sm" removable onRemove={() => removeTag(tag)}>
                {tag}
              </Badge>
            ))}
          </div>
        )}
      </FormField>

      <div className="flex justify-end gap-3 pt-2">
        <Button type="button" variant="secondary" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" isLoading={isLoading}>
          {initialData ? "Update Project" : "Create Project"}
        </Button>
      </div>
    </form>
  );
}
