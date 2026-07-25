interface StatusBadgeProps {
  status: "success" | "error" | "warning" | "info" | "idle" | "running";
  label?: string;
}

const STATUS_STYLES = {
  success: "bg-green-100 text-green-800",
  error: "bg-red-100 text-red-800",
  warning: "bg-yellow-100 text-yellow-800",
  info: "bg-blue-100 text-blue-800",
  idle: "bg-gray-100 text-gray-800",
  running: "bg-purple-100 text-purple-800",
};

const STATUS_LABELS = {
  success: "Sucesso",
  error: "Erro",
  warning: "Aviso",
  info: "Info",
  idle: "Ocioso",
  running: "Executando",
};

export function StatusBadge({ status, label }: StatusBadgeProps) {
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${STATUS_STYLES[status]}`}
    >
      {label || STATUS_LABELS[status]}
    </span>
  );
}
