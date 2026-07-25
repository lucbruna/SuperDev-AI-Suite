"use client";

import { useState, useCallback, type FormEvent } from "react";
import { Input } from "@/components/inputs/Input";
import { FormField } from "@/components/forms/FormField";
import { Button } from "@/components/buttons/Button";

interface OrganizationFormData {
  name: string;
  slug: string;
  description: string;
  website: string;
  logo_url: string;
}

interface OrganizationFormProps {
  initialData?: Partial<OrganizationFormData>;
  onSubmit: (data: OrganizationFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, "")
    .replace(/[\s_]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function OrganizationForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading,
}: OrganizationFormProps) {
  const [name, setName] = useState(initialData?.name ?? "");
  const [slug, setSlug] = useState(initialData?.slug ?? "");
  const [description, setDescription] = useState(initialData?.description ?? "");
  const [website, setWebsite] = useState(initialData?.website ?? "");
  const [logoUrl, setLogoUrl] = useState(initialData?.logo_url ?? "");
  const [slugEdited, setSlugEdited] = useState(!!initialData?.slug);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleNameChange = useCallback(
    (value: string) => {
      setName(value);
      if (!slugEdited) {
        setSlug(slugify(value));
      }
    },
    [slugEdited],
  );

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    if (!name.trim()) errs.name = "Organization name is required";
    if (!slug.trim()) errs.slug = "Slug is required";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    onSubmit({
      name: name.trim(),
      slug: slug.trim(),
      description: description.trim(),
      website: website.trim(),
      logo_url: logoUrl.trim(),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <Input
        label="Organization Name"
        placeholder="My Organization"
        value={name}
        onChange={(e) => handleNameChange(e.target.value)}
        error={errors.name}
        autoFocus
      />

      <Input
        label="Slug"
        placeholder="my-organization"
        value={slug}
        onChange={(e) => {
          setSlugEdited(true);
          setSlug(e.target.value);
        }}
        error={errors.slug}
        hint="Auto-generated from name. Used in URLs."
      />

      <FormField label="Description">
        <textarea
          className="flex min-h-[80px] w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-sm text-surface-900 placeholder:text-surface-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-0 dark:bg-surface-900 dark:text-surface-100 dark:border-surface-600 dark:focus:ring-primary-400"
          placeholder="Describe your organization"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </FormField>

      <Input
        label="Website"
        type="url"
        placeholder="https://example.com"
        value={website}
        onChange={(e) => setWebsite(e.target.value)}
      />

      <Input
        label="Logo URL"
        type="url"
        placeholder="https://example.com/logo.png"
        value={logoUrl}
        onChange={(e) => setLogoUrl(e.target.value)}
      />

      <div className="flex justify-end gap-3 pt-2">
        <Button type="button" variant="secondary" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" isLoading={isLoading}>
          {initialData ? "Update Organization" : "Create Organization"}
        </Button>
      </div>
    </form>
  );
}
