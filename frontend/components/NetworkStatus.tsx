"use client";

import { useEffect, useState } from "react";

export default function NetworkStatus() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    // Definimos el estado actual al montar
    setIsOnline(navigator.onLine);

    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  if (isOnline) return null;

  return (
    <div className="fixed top-0 left-0 w-full z-[9999] bg-red-600 text-white text-center py-2 px-4 shadow-lg flex justify-center items-center gap-2 animate-in slide-in-from-top duration-300">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-5 w-5"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={2}
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M13 10V3L4 14h7v7l9-11h-7z"
        />
      </svg>
      <span className="font-medium text-sm">
        Sin conexión a Internet. Estás navegando en modo offline.
      </span>
    </div>
  );
}
