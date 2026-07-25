"use client";

import { useEffect, useState, useRef, type ReactNode } from "react";

interface LazyLoadProps {
  children: ReactNode;
  threshold?: number;
  placeholder?: ReactNode;
}

export function LazyLoad({ children, threshold = 0.1, placeholder }: LazyLoadProps) {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [threshold]);

  return (
    <div ref={ref}>
      {isVisible ? (
        children
      ) : (
        placeholder || <div className="h-32 animate-pulse bg-muted rounded-lg" />
      )}
    </div>
  );
}