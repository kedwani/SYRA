'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { isAuthenticated, getUser, clearAuth } from '@/lib/auth';
import { useEffect, useState } from 'react';
import { User } from '@/types';

export default function Navbar() {
  const router = useRouter();
  const [loggedIn, setLoggedIn] = useState(false);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    setLoggedIn(isAuthenticated());
    setUser(getUser());
  }, []);

  const handleLogout = () => {
    clearAuth();
    setLoggedIn(false);
    setUser(null);
    router.push('/');
  };

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link href="/" className="text-xl font-bold text-red-600">
          SYRA
        </Link>

        <div className="flex items-center gap-4">
          {loggedIn ? (
            <>
              <Link href="/dashboard" className="text-gray-700 hover:text-red-600 text-sm font-medium">
                Dashboard
              </Link>
              <Link href="/medical" className="text-gray-700 hover:text-red-600 text-sm font-medium">
                Medical
              </Link>
              <Link href="/profile" className="text-gray-700 hover:text-red-600 text-sm font-medium">
                Profile
              </Link>
              <Link href="/bracelets" className="text-gray-700 hover:text-red-600 text-sm font-medium">
                Bracelets
              </Link>
              <span className="text-sm text-gray-500">
                {user?.full_name || user?.email}
              </span>
              <button
                onClick={handleLogout}
                className="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link
                href="/auth/login"
                className="text-sm text-gray-700 hover:text-red-600 font-medium"
              >
                Login
              </Link>
              <Link
                href="/auth/register"
                className="text-sm bg-red-600 hover:bg-red-700 text-white px-4 py-1.5 rounded font-medium"
              >
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
