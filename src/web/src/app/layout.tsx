import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "spec2cloud — Python",
  description: "spec2cloud shell — Python",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
