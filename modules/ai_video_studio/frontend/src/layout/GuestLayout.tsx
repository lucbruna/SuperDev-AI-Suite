import { Outlet } from 'react-router-dom';
import { Clapperboard } from 'lucide-react';
import { APP_NAME } from '@/constants';

export default function GuestLayout() {
  return (
    <div className="grid min-h-screen place-items-center bg-surface p-6">
      <div className="absolute top-6 left-6 flex items-center gap-2">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-white">
          <Clapperboard className="h-4 w-4" />
        </span>
        <span className="text-sm font-semibold text-content">{APP_NAME}</span>
      </div>
      <div className="w-full max-w-md">
        <Outlet />
      </div>
    </div>
  );
}
