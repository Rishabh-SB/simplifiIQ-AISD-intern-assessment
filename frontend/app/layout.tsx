import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SimplifIQ | Lead Audit Engine",
  description: "Automated Lead Enrichment Pipeline",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full bg-slate-900">
      <body className="h-full font-sans antialiased text-slate-100 relative overflow-x-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-blue-900/20 via-slate-900 to-slate-900 -z-10" />
        <main className="min-h-screen flex items-center justify-center p-4 md:p-8">
          {children}
        </main>
      </body>
    </html>
  );
}
