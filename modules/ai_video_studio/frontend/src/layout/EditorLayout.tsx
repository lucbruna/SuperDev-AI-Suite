import { Outlet } from 'react-router-dom';
import StatusBar from '@/layout/StatusBar';
import Toolbar from '@/layout/Toolbar';

export default function EditorLayout() {
  return (
    <div className="flex h-screen flex-col overflow-hidden bg-surface">
      <Toolbar />
      <main className="min-h-0 flex-1 overflow-hidden">
        <Outlet />
      </main>
      <StatusBar />
    </div>
  );
}
