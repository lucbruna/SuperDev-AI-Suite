"use client";

import { useEffect, useState, type ReactNode } from "react";

interface MobileLayoutProps {
  children: ReactNode;
}

export function MobileLayout({ children }: MobileLayoutProps) {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < 768);
    check();
    window.addEventListener("resize", check);
    return () => window.removeEventListener("resize", check);
  }, []);

  if (isMobile) {
    return (
      <div className="min-h-screen bg-background">
        <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur px-4 py-3">
          <h1 className="text-lg font-bold">SuperDev</h1>
        </header>
        <main className="px-4 py-4 space-y-4">{children}</main>
        <nav className="fixed bottom-0 w-full border-t bg-background flex justify-around py-2">
          {["Dashboard", "Projects", "Agents", "Settings"].map((item) => (
            <a
              key={item}
              href={`/${item.toLowerCase()}`}
              className="text-xs text-center text-muted-foreground hover:text-primary"
            >
              {item}
            </a>
          ))}
        </nav>
      </div>
    );
  }

  return <>{children}</>;
}