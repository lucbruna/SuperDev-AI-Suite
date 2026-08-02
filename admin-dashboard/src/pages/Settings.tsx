import { User, Mail, Shield, Calendar, LogOut } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { formatDate } from '../lib/utils';

/** Página de configurações — perfil do usuário autenticado + ações da conta. */
export function Settings() {
  const { user, logout } = useAuth();

  const initials = (user?.fullName || user?.username || user?.email || 'U')
    .split(/[\s@.]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0]!.toUpperCase())
    .join('');

  const fields = [
    { icon: User, label: 'Nome de usuário', value: user?.username },
    { icon: User, label: 'Nome completo', value: user?.fullName ?? '—' },
    { icon: Mail, label: 'E-mail', value: user?.email },
    { icon: Shield, label: 'Função', value: user?.role ?? 'membro' },
    { icon: Calendar, label: 'Conta criada em', value: user?.createdAt ? formatDate(user.createdAt) : '—' },
  ];

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="page-header">
        <div>
          <h1 className="page-title">Configurações</h1>
          <p className="page-subtitle">Sua conta e preferências no SuperDev</p>
        </div>
      </div>

      {/* Perfil */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Perfil</h3>
          <span className="badge-info">{user?.role ?? 'membro'}</span>
        </div>
        <div className="card-body">
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 text-xl font-bold text-white">
              {initials}
            </div>
            <div>
              <p className="text-lg font-semibold text-ink">
                {user?.fullName || user?.username || 'Usuário'}
              </p>
              <p className="text-sm text-ink-muted">{user?.email}</p>
              {user?.isEmailVerified === false && (
                <span className="badge-warning mt-1">E-mail não verificado</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Detalhes */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Detalhes da conta</h3>
        </div>
        <div className="card-body">
          <dl className="divide-y divide-line">
            {fields.map((f) => (
              <div key={f.label} className="flex items-center gap-4 py-3">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-surface-alt text-ink-muted">
                  <f.icon className="h-4 w-4" />
                </div>
                <dt className="w-44 shrink-0 text-sm text-ink-muted">{f.label}</dt>
                <dd className="min-w-0 flex-1 truncate text-sm font-medium text-ink">{f.value ?? '—'}</dd>
              </div>
            ))}
          </dl>
        </div>
      </div>

      {/* Sessão */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Sessão</h3>
        </div>
        <div className="card-body flex items-center justify-between gap-4">
          <p className="text-sm text-ink-muted">
            Encerre a sessão atual. Você precisará fazer login novamente para acessar o painel.
          </p>
          <button onClick={() => void logout()} className="btn-danger shrink-0">
            <LogOut className="h-4 w-4" /> Sair da conta
          </button>
        </div>
      </div>
    </div>
  );
}

export default Settings;
