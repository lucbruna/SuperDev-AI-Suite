import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "@/styles/globals.css";
import { AppProvider } from "@/providers/AppProvider";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "SuperDev AI Suite",
    template: "%s | SuperDev AI Suite",
  },
  description:
    "AI-powered development suite for supercharging your workflow with intelligent tools and automation.",
  keywords: ["development", "AI", "suite", "tools", "productivity"],
  authors: [{ name: "SuperDev" }],
  manifest: "/manifest.json",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
    apple: "/icons/icon-192x192.png",
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "/",
    title: "SuperDev AI Suite",
    description:
      "AI-powered development suite for supercharging your workflow with intelligent tools and automation.",
    siteName: "SuperDev AI Suite",
  },
  twitter: {
    card: "summary_large_image",
    title: "SuperDev AI Suite",
    description:
      "AI-powered development suite for supercharging your workflow with intelligent tools and automation.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" suppressHydrationWarning className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="min-h-screen bg-white font-sans text-surface-900 antialiased dark:bg-surface-950 dark:text-surface-100">
        <AppProvider>{children}</AppProvider>
      </body>
    </html>
  );
}
