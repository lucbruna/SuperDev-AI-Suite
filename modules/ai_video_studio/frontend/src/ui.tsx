import type {
  ButtonHTMLAttributes,
  HTMLAttributes,
  InputHTMLAttributes,
  ReactNode,
  SelectHTMLAttributes,
  TextareaHTMLAttributes,
} from 'react';
import type { LucideIcon } from 'lucide-react';
import { cn } from '@/utils';

/* ---------------------------------- Button --------------------------------- */

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline';
type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
}

const buttonVariants: Record<ButtonVariant, string> = {
  primary: 'bg-primary text-white shadow-sm hover:bg-primary/90',
  secondary: 'border border-border bg-panel text-content hover:bg-surface',
  ghost: 'bg-transparent text-content hover:bg-panel',
  danger: 'bg-red-600 text-white hover:bg-red-500',
  outline: 'border border-primary text-primary hover:bg-primary/10',
};

const buttonSizes: Record<ButtonSize, string> = {
  sm: 'h-8 rounded-lg px-3 text-sm',
  md: 'h-9 rounded-lg px-4 text-sm',
  lg: 'h-11 rounded-xl px-6 text-base',
};

export function Button({ variant = 'primary', size = 'md', className, type = 'button', ...rest }: ButtonProps) {
  return (
    <button
      type={type}
      className={cn(
        'inline-flex items-center justify-center gap-2 font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 disabled:pointer-events-none disabled:opacity-50',
        buttonVariants[variant],
        buttonSizes[size],
        className,
      )}
      {...rest}
    />
  );
}

export interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  icon: LucideIcon;
  label: string;
  size?: 'sm' | 'md';
}

export function IconButton({ icon: Icon, label, size = 'md', className, type = 'button', ...rest }: IconButtonProps) {
  return (
    <button
      type={type}
      aria-label={label}
      title={label}
      className={cn(
        'inline-flex items-center justify-center rounded-lg text-subtle transition-colors hover:bg-panel hover:text-content focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 disabled:pointer-events-none disabled:opacity-50',
        size === 'sm' ? 'h-7 w-7' : 'h-9 w-9',
        className,
      )}
      {...rest}
    >
      <Icon className={size === 'sm' ? 'h-4 w-4' : 'h-5 w-5'} />
    </button>
  );
}

/* ----------------------------------- Card ---------------------------------- */

export function Card({ className, ...rest }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('rounded-xl border border-border bg-panel', className)} {...rest} />;
}

export interface CardHeaderProps {
  title?: string;
  subtitle?: string;
  action?: ReactNode;
  className?: string;
  children?: ReactNode;
}

export function CardHeader({ title, subtitle, action, className, children }: CardHeaderProps) {
  return (
    <div className={cn('flex items-start justify-between gap-3 border-b border-border px-5 py-4', className)}>
      <div className="min-w-0">
        {title ? <h3 className="text-sm font-semibold text-content">{title}</h3> : null}
        {subtitle ? <p className="mt-0.5 text-xs text-subtle">{subtitle}</p> : null}
        {children}
      </div>
      {action ? <div className="shrink-0">{action}</div> : null}
    </div>
  );
}

export function CardBody({ className, ...rest }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('p-5', className)} {...rest} />;
}

export function CardFooter({ className, ...rest }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('border-t border-border px-5 py-3', className)} {...rest} />;
}

/* ---------------------------------- Badge ---------------------------------- */

export interface BadgeProps {
  variant?: 'default' | 'accent' | 'success' | 'warning' | 'danger' | 'info' | 'neutral';
  className?: string;
  children?: ReactNode;
}

const badgeVariants: Record<NonNullable<BadgeProps['variant']>, string> = {
  default: 'bg-primary/15 text-primary',
  accent: 'bg-accent/15 text-accent',
  success: 'bg-emerald-500/15 text-emerald-500',
  warning: 'bg-amber-500/15 text-amber-500',
  danger: 'bg-red-500/15 text-red-500',
  info: 'bg-sky-500/15 text-sky-500',
  neutral: 'bg-border/50 text-subtle',
};

export function Badge({ variant = 'default', className, children }: BadgeProps) {
  return (
    <span className={cn('inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium', badgeVariants[variant], className)}>
      {children}
    </span>
  );
}

/* ------------------------------- SectionHeader ------------------------------ */

export interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  className?: string;
}

export function SectionHeader({ title, subtitle, action, className }: SectionHeaderProps) {
  return (
    <div className={cn('mb-6 flex flex-wrap items-end justify-between gap-4', className)}>
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-content">{title}</h1>
        {subtitle ? <p className="mt-1 text-sm text-subtle">{subtitle}</p> : null}
      </div>
      {action ? <div className="flex items-center gap-2">{action}</div> : null}
    </div>
  );
}

/* -------------------------------- ProgressBar ------------------------------ */

export interface ProgressBarProps {
  value: number;
  variant?: 'default' | 'accent' | 'danger';
  className?: string;
}

export function ProgressBar({ value, variant = 'default', className }: ProgressBarProps) {
  const clamped = Math.max(0, Math.min(100, value));
  const fill = variant === 'accent' ? 'bg-accent' : variant === 'danger' ? 'bg-red-500' : 'bg-primary';
  return (
    <div className={cn('h-2 w-full overflow-hidden rounded-full bg-border/50', className)}>
      <div className={cn('h-full rounded-full transition-all', fill)} style={{ width: `${clamped}%` }} />
    </div>
  );
}

/* ---------------------------------- Fields --------------------------------- */

export interface FieldProps {
  label?: string;
  hint?: string;
  error?: string;
  className?: string;
  children?: ReactNode;
}

export function Field({ label, hint, error, className, children }: FieldProps) {
  return (
    <label className={cn('block', className)}>
      {label ? <span className="mb-1.5 block text-sm font-medium text-content">{label}</span> : null}
      {children}
      {error ? <span className="mt-1 block text-xs text-red-500">{error}</span> : null}
      {!error && hint ? <span className="mt-1 block text-xs text-subtle">{hint}</span> : null}
    </label>
  );
}

const controlClasses =
  'w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-content placeholder:text-subtle/70 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30 disabled:opacity-50';

export function Input({ className, ...rest }: InputHTMLAttributes<HTMLInputElement>) {
  return <input className={cn(controlClasses, className)} {...rest} />;
}

export function Textarea({ className, ...rest }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className={cn(controlClasses, 'min-h-24 resize-y', className)} {...rest} />;
}

export function Select({ className, children, ...rest }: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select className={cn(controlClasses, 'cursor-pointer', className)} {...rest}>
      {children}
    </select>
  );
}

/* ---------------------------------- Switch --------------------------------- */

export interface SwitchProps {
  checked: boolean;
  onChange: (value: boolean) => void;
  label?: string;
  className?: string;
}

export function Switch({ checked, onChange, label, className }: SwitchProps) {
  return (
    <button type="button" role="switch" aria-checked={checked} onClick={() => onChange(!checked)} className={cn('flex items-center gap-3', className)}>
      <span className={cn('relative h-5 w-9 shrink-0 rounded-full transition-colors', checked ? 'bg-primary' : 'bg-border')}>
        <span
          className={cn(
            'absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform',
            checked ? 'translate-x-4' : 'translate-x-0.5',
          )}
        />
      </span>
      {label ? <span className="text-sm text-content">{label}</span> : null}
    </button>
  );
}

/* ---------------------------------- Avatar --------------------------------- */

export interface AvatarProps {
  name: string;
  src?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const avatarSizes = {
  sm: 'h-6 w-6 text-[10px]',
  md: 'h-9 w-9 text-xs',
  lg: 'h-12 w-12 text-base',
};

function initialsFor(name: string): string {
  return name
    .split(/\s+/)
    .map((part) => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();
}

export function Avatar({ name, src, size = 'md', className }: AvatarProps) {
  if (src) {
    return <img src={src} alt={name} className={cn('rounded-full object-cover', avatarSizes[size], className)} />;
  }
  const hue = [...name].reduce((acc, char) => acc + char.charCodeAt(0), 0) % 360;
  return (
    <span
      className={cn('inline-flex shrink-0 items-center justify-center rounded-full font-semibold text-white', avatarSizes[size], className)}
      style={{ backgroundColor: `hsl(${hue} 45% 45%)` }}
    >
      {initialsFor(name)}
    </span>
  );
}

/* --------------------------------- Spinner --------------------------------- */

export interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const spinnerSizes = {
  sm: 'h-4 w-4 border-2',
  md: 'h-6 w-6 border-2',
  lg: 'h-10 w-10 border-[3px]',
};

export function Spinner({ size = 'md', className }: SpinnerProps) {
  return (
    <span
      role="status"
      aria-label="Loading"
      className={cn('inline-block animate-spin rounded-full border-current border-t-transparent text-primary', spinnerSizes[size], className)}
    />
  );
}

/* -------------------------------- EmptyState ------------------------------- */

export interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}

export function EmptyState({ icon: Icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-border px-6 py-12 text-center', className)}>
      {Icon ? <Icon className="h-10 w-10 text-subtle" /> : null}
      <p className="font-medium text-content">{title}</p>
      {description ? <p className="max-w-sm text-sm text-subtle">{description}</p> : null}
      {action ? <div className="mt-2">{action}</div> : null}
    </div>
  );
}

/* --------------------------------- StatCard -------------------------------- */

export interface StatCardProps {
  label: string;
  value: string | number;
  icon?: LucideIcon;
  trend?: 'up' | 'down' | 'flat';
  delta?: string;
  className?: string;
}

export function StatCard({ label, value, icon: Icon, trend, delta, className }: StatCardProps) {
  return (
    <Card className={cn('p-5', className)}>
      <div className="flex items-center justify-between gap-2">
        <span className="text-sm text-subtle">{label}</span>
        {Icon ? <Icon className="h-5 w-5 shrink-0 text-primary" /> : null}
      </div>
      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-2xl font-semibold text-content">{value}</span>
        {trend && delta ? (
          <span
            className={cn(
              'text-xs font-medium',
              trend === 'up' ? 'text-emerald-500' : trend === 'down' ? 'text-red-500' : 'text-subtle',
            )}
          >
            {trend === 'up' ? '▲' : trend === 'down' ? '▼' : '■'} {delta}
          </span>
        ) : null}
      </div>
    </Card>
  );
}

/* ----------------------------------- Tabs ---------------------------------- */

export interface TabsProps {
  tabs: { id: string; label: string }[];
  value: string;
  onChange: (id: string) => void;
  className?: string;
}

export function Tabs({ tabs, value, onChange, className }: TabsProps) {
  return (
    <div className={cn('inline-flex items-center gap-1 rounded-lg border border-border bg-panel p-1', className)}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          onClick={() => onChange(tab.id)}
          className={cn(
            'rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
            value === tab.id ? 'bg-primary text-white' : 'text-subtle hover:text-content',
          )}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}

/* --------------------------------- Divider --------------------------------- */

export function Divider({ className }: { className?: string }) {
  return <div className={cn('h-px w-full bg-border', className)} />;
}
