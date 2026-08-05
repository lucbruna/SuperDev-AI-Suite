import { APP_NAME, APP_VERSION } from '@/constants';

export default function Footer() {
  return (
    <footer className="py-6 text-center text-xs text-subtle">
      © {new Date().getFullYear()} {APP_NAME} · v{APP_VERSION}
    </footer>
  );
}
