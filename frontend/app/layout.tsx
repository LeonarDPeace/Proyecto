import type { Metadata, Viewport } from "next";
import "@/styles/globals.css";
import NetworkStatus from "@/components/NetworkStatus";

export const metadata: Metadata = {
  title: "VeraMarket — Marketplace Universitario",
  description:
    "Compra y vende dentro de tu campus universitario. Conecta con emprendedores verificados en Cali, Colombia.",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "VeraMarket",
  },
};

export const viewport: Viewport = {
  themeColor: "#2563eb",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es-CO">
      <body className="min-h-screen bg-white antialiased">
        <NetworkStatus />
        {children}
      </body>
    </html>
  );
}
