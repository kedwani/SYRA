'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/auth';
import { getMyBracelets, claimBracelet } from '@/lib/api';
import { Bracelet } from '@/types';
import FormInput from '@/components/FormInput';

export default function BraceletsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [bracelets, setBracelets] = useState<Bracelet[]>([]);
  const [showClaim, setShowClaim] = useState(false);
  const [serial, setSerial] = useState('');
  const [pin, setPin] = useState('');
  const [claiming, setClaiming] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/auth/login');
      return;
    }

    getMyBracelets()
      .then(setBracelets)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  const handleClaim = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setClaiming(true);

    try {
      const result = await claimBracelet({ serial_number: serial, claim_pin: pin });
      setSuccess(result.message);
      setBracelets(await getMyBracelets());
      setShowClaim(false);
      setSerial('');
      setPin('');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Claim failed';
      setError(message);
    } finally {
      setClaiming(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <p className="text-gray-500">Loading bracelets...</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Bracelets</h1>
        <button
          onClick={() => setShowClaim(!showClaim)}
          className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm font-medium"
        >
          {showClaim ? 'Cancel' : 'Claim Bracelet'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded px-4 py-3 mb-4">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 text-sm rounded px-4 py-3 mb-4">
          {success}
        </div>
      )}

      {showClaim && (
        <form onSubmit={handleClaim} className="bg-white border border-gray-200 rounded-lg p-5 mb-6">
          <h2 className="text-sm font-semibold mb-4">Claim a Bracelet</h2>
          <p className="text-xs text-gray-500 mb-4">
            Enter the serial number and claim PIN found on your bracelet packaging.
          </p>
          <div className="space-y-4">
            <FormInput
              label="Serial Number"
              value={serial}
              onChange={setSerial}
              required
              id="br-serial"
              placeholder="e.g. SYRA-A1B2C3D4"
            />
            <FormInput
              label="Claim PIN (6 digits)"
              value={pin}
              onChange={setPin}
              required
              id="br-pin"
              placeholder="e.g. 123456"
            />
            <button
              type="submit"
              disabled={claiming}
              className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded text-sm font-medium disabled:opacity-50"
            >
              {claiming ? 'Claiming...' : 'Claim'}
            </button>
          </div>
        </form>
      )}

      {bracelets.length === 0 ? (
        <div className="bg-white border border-gray-200 rounded-lg p-6 text-center">
          <p className="text-gray-500 text-sm mb-2">No bracelets linked to your profile.</p>
          <p className="text-xs text-gray-400">
            Purchase a SYRA bracelet and claim it using the serial number and PIN.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {bracelets.map((b) => (
            <div key={b.id} className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">{b.serial_number}</p>
                  <p className="text-xs text-gray-500">
                    Status: <span className={`font-medium ${
                      b.status === 'active' ? 'text-green-600' :
                      b.status === 'claimed' ? 'text-blue-600' :
                      b.status === 'lost' ? 'text-red-600' : 'text-gray-600'
                    }`}>{b.status}</span>
                  </p>
                  {b.claimed_at && (
                    <p className="text-xs text-gray-400">
                      Claimed: {new Date(b.claimed_at).toLocaleDateString()}
                    </p>
                  )}
                </div>
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                  b.status === 'active' ? 'bg-green-100 text-green-700' :
                  b.status === 'claimed' ? 'bg-blue-100 text-blue-700' :
                  b.status === 'lost' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'
                }`}>
                  {b.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
