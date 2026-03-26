'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, getUser } from '@/lib/auth';
import { getMyProfile, updateMyProfile, getQRCode } from '@/lib/api';
import { MedicalProfile, QRCodeData } from '@/types';
import FormInput from '@/components/FormInput';
import FormSelect from '@/components/FormSelect';

const BLOOD_TYPES = [
  { value: 'UNKNOWN', label: 'Unknown' },
  { value: 'A+', label: 'A+' },
  { value: 'A-', label: 'A-' },
  { value: 'B+', label: 'B+' },
  { value: 'B-', label: 'B-' },
  { value: 'AB+', label: 'AB+' },
  { value: 'AB-', label: 'AB-' },
  { value: 'O+', label: 'O+' },
  { value: 'O-', label: 'O-' },
];

const VISIBILITY_OPTIONS = [
  { value: 'public', label: 'Public - Anyone' },
  { value: 'medical', label: 'Medical Personnel Only' },
  { value: 'private', label: 'Private - Owner Only' },
];

export default function ProfilePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<MedicalProfile | null>(null);
  const [qr, setQr] = useState<QRCodeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [phone, setPhone] = useState('');
  const [dob, setDob] = useState('');
  const [bloodType, setBloodType] = useState('UNKNOWN');
  const [visibility, setVisibility] = useState('public');
  const [emergencyNote, setEmergencyNote] = useState('');

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/auth/login');
      return;
    }

    Promise.all([getMyProfile(), getQRCode()])
      .then(([p, q]) => {
        setProfile(p);
        setQr(q);
        setFirstName(p.user.first_name || '');
        setLastName(p.user.last_name || '');
        setPhone(p.user.phone || '');
        setDob(p.user.date_of_birth || '');
        setBloodType(p.user.blood_type || 'UNKNOWN');
        setVisibility(p.default_visibility || 'public');
        setEmergencyNote(p.emergency_note || '');
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSaving(true);

    try {
      const updated = await updateMyProfile({
        default_visibility: visibility,
        emergency_note: emergencyNote,
      } as unknown as MedicalProfile);
      setProfile(updated);
      setSuccess('Profile updated successfully');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Update failed';
      setError(message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <p className="text-gray-500">Loading profile...</p>
      </div>
    );
  }

  const user = getUser();

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Profile</h1>

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

      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">User Information</h2>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <FormInput
              label="First Name"
              value={firstName}
              onChange={setFirstName}
              id="prof-first"
            />
            <FormInput
              label="Last Name"
              value={lastName}
              onChange={setLastName}
              id="prof-last"
            />
          </div>
          <FormInput
            label="Email"
            value={user?.email || ''}
            onChange={() => {}}
            id="prof-email"
          />
          <FormInput
            label="Phone"
            type="tel"
            value={phone}
            onChange={setPhone}
            id="prof-phone"
          />
          <FormInput
            label="Date of Birth"
            type="date"
            value={dob}
            onChange={setDob}
            id="prof-dob"
          />
          <FormSelect
            label="Blood Type"
            value={bloodType}
            onChange={setBloodType}
            options={BLOOD_TYPES}
            id="prof-blood"
          />
        </div>
      </div>

      <form onSubmit={handleSave} className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Profile Settings</h2>
        <div className="space-y-4">
          <FormSelect
            label="Default Visibility"
            value={visibility}
            onChange={setVisibility}
            options={VISIBILITY_OPTIONS}
            id="prof-visibility"
          />
          <div>
            <label htmlFor="prof-note" className="block text-sm font-medium text-gray-700 mb-1">
              Emergency Note
            </label>
            <textarea
              id="prof-note"
              value={emergencyNote}
              onChange={(e) => setEmergencyNote(e.target.value)}
              placeholder="Important information for emergencies (e.g., 'Diabetic - Type 1')"
              rows={3}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent text-gray-900"
            />
          </div>
          <button
            type="submit"
            disabled={saving}
            className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded font-medium text-sm disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </form>

      {qr && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">QR Code</h2>
          {qr.qr_image && (
            <img
              src={qr.qr_image}
              alt="QR Code"
              className="w-48 h-48 border border-gray-200 rounded mb-3"
            />
          )}
          <p className="text-xs text-gray-400 break-all">
            Token: {qr.qr_token_hash}
          </p>
        </div>
      )}
    </div>
  );
}
