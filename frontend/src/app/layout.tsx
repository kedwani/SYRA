import type { Metadata } from 'next';
import './globals.css';
import RootProviders from './providers';

export const metadata: Metadata = {
  title: 'SYRA Medical ID',
  description: 'Medical emergency identification and alert system',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <RootProviders>
      {children}
    </RootProviders>
  );
}
