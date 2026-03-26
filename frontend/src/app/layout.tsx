import type { Metadata } from "next";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "SYRA Medical ID",
  description: "Medical emergency identification and alert system",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body><main>{children}</main></body>
    </html>
  );
}
