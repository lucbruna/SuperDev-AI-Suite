"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

/**
 * /chat redirects to /llm/chat (the functional LLM chat page).
 * This route exists because the sidebar links to /chat.
 */
export default function ChatRedirectPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/llm/chat");
  }, [router]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <p className="text-surface-400">Redirecting to LLM Chat...</p>
    </div>
  );
}
