'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { getUser, isAuthenticated } from '@/lib/auth';
import { getMyProfile, getQRCode } from '@/lib/api';
import { User, MedicalProfile, QRCodeData } from '@/types';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<MedicalProfile | null>(null);
  const [qr, setQr] = useState<QRCodeData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/auth/login');
      return;
    }

    const u = getUser();
    setUser(u);

    Promise.all([getMyProfile(), getQRCode()])
      .then(([p, q]) => {
        setProfile(p);
        setQr(q);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <h2 className="text-lg font-semibold mb-2">
          Welcome, {user?.full_name || user?.email}
        </h2>
        <p className="text-sm text-gray-500 mb-4">
          {user?.email} &middot; Blood type: {user?.blood_type || 'Unknown'}
        </p>

        {profile?.emergency_note && (
          <div className="bg-yellow-50 border border-yellow-200 rounded px-4 py-3 text-sm text-yellow-800 mb-4">
            <strong>Emergency Note:</strong> {profile.emergency_note}
          </div>
        )}

        <div className="flex flex-wrap gap-3">
          <Link
            href="/profile"
            className="bg-gray-100 hover:bg-gray-200 text-gray-800 px-4 py-2 rounded text-sm font-medium"
          >
            Edit Profile
          </Link>
          <Link
            href="/medical"
            className="bg-gray-100 hover:bg-gray-200 text-gray-800 px-4 py-2 rounded text-sm font-medium"
          >
            Medical Info
          </Link>
          <Link
            href="/bracelets"
            className="bg-gray-100 hover:bg-gray-200 text-gray-800 px-4 py-2 rounded text-sm font-medium"
          >
            Bracelets
          </Link>
        </div>
      </div>

      {qr && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Your QR Code</h2>
          <div className="flex flex-col sm:flex-row gap-6 items-start">
            {qr.qr_image && (
              <img
                src={qr.qr_image}
                alt="QR Code"
                className="w-40 h-40 border border-gray-200 rounded"
              />
            )}
            <div>
              <p className="text-sm text-gray-600 mb-2">
                Scan this QR code to access your emergency information.
              </p>
              <p className="text-xs text-gray-400 break-all mb-2">
                Emergency URL: {qr.qr_url}
              </p>
              <Link
                href={`/e/${qr.qr_token_hash}`}
                className="text-sm text-red-600 hover:text-red-700 font-medium"
                target="_blank"
              >
                View Emergency Page &rarr;
              </Link>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-1">Allergies</h3>
          <Link href="/medical" className="text-xs text-red-600 hover:text-red-700">
            Manage &rarr;
          </Link>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-1">Medications</h3>
          <Link href="/medical" className="text-xs text-red-600 hover:text-red-700">
            Manage &rarr;
          </Link>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-1">Emergency Contacts</h3>
          <Link href="/medical" className="text-xs text-red-600 hover:text-red-700">
            Manage &rarr;
          </Link>
        </div>
      </div>
    </div>
  );
}
