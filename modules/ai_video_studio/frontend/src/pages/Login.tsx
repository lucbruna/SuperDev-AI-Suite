import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clapperboard } from 'lucide-react';
import { APP_NAME } from '@/constants';
import { useAppStore } from '@/store';
import { Button, Card, Divider, Field, Input } from '@/ui';
import type { User } from '@/types';

export default function Login() {
  const navigate = useNavigate();
  const setUser = useAppStore((state) => state.setUser);
  const [email, setEmail] = useState('ana@superdev.app');
  const [password, setPassword] = useState('');

  const signIn = () => {
    const user: User = {
      id: 'u1',
      name: 'Ana Souza',
      email,
      role: 'owner',
      status: 'active',
      lastActive: new Date().toISOString(),
    };
    setUser(user);
    navigate('/dashboard');
  };

  return (
    <Card className="p-8">
      <div className="mb-6 flex flex-col items-center text-center">
        <span className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-white">
          <Clapperboard className="h-6 w-6" />
        </span>
        <h1 className="text-xl font-semibold text-content">{APP_NAME}</h1>
        <p className="mt-1 text-sm text-subtle">Sign in to your workspace</p>
      </div>
      <div className="space-y-4">
        <Field label="Email">
          <Input type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@company.app" />
        </Field>
        <Field label="Password" hint="Demo — any password works">
          <Input type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="••••••••" />
        </Field>
        <Button className="w-full" size="lg" onClick={signIn}>
          Sign in
        </Button>
        <Divider />
        <Button variant="ghost" className="w-full" onClick={() => navigate('/dashboard')}>
          Continue as guest
        </Button>
      </div>
    </Card>
  );
}
