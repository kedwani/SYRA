'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { register } from '@/lib/api';
import { setAuth } from '@/lib/auth';
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

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    email: '',
    username: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    phone: '',
    date_of_birth: '',
    blood_type: 'UNKNOWN',
  });
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [privacyConsent, setPrivacyConsent] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const update = (field: string) => (value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!agreedToTerms || !privacyConsent) {
      setError('You must agree to the terms and privacy policy');
      return;
    }

    setLoading(true);

    try {
      const data = await register({
        ...form,
        agreed_to_terms: agreedToTerms,
        privacy_consent: privacyConsent,
      });
      setAuth(data.access, data.refresh, data.user);
      router.push('/dashboard');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Registration failed';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-57px)] flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md">
        <h1 className="text-2xl font-bold text-center mb-6">Create Account</h1>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded px-4 py-3 mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <FormInput
              label="First Name"
              value={form.first_name}
              onChange={update('first_name')}
              placeholder="John"
              id="reg-first"
            />
            <FormInput
              label="Last Name"
              value={form.last_name}
              onChange={update('last_name')}
              placeholder="Doe"
              id="reg-last"
            />
          </div>

          <FormInput
            label="Email"
            type="email"
            value={form.email}
            onChange={update('email')}
            placeholder="you@example.com"
            required
            id="reg-email"
          />

          <FormInput
            label="Username"
            value={form.username}
            onChange={update('username')}
            placeholder="johndoe"
            required
            id="reg-username"
          />

          <FormInput
            label="Phone"
            type="tel"
            value={form.phone}
            onChange={update('phone')}
            placeholder="+1234567890"
            id="reg-phone"
          />

          <FormInput
            label="Date of Birth"
            type="date"
            value={form.date_of_birth}
            onChange={update('date_of_birth')}
            id="reg-dob"
          />

          <FormSelect
            label="Blood Type"
            value={form.blood_type}
            onChange={update('blood_type')}
            options={BLOOD_TYPES}
            id="reg-blood"
          />

          <FormInput
            label="Password"
            type="password"
            value={form.password}
            onChange={update('password')}
            placeholder="Min 8 characters"
            required
            id="reg-password"
          />

          <FormInput
            label="Confirm Password"
            type="password"
            value={form.password_confirm}
            onChange={update('password_confirm')}
            placeholder="Repeat password"
            required
            id="reg-password-confirm"
          />

          <div className="space-y-2">
            <label className="flex items-start gap-2 text-sm">
              <input
                type="checkbox"
                checked={agreedToTerms}
                onChange={(e) => setAgreedToTerms(e.target.checked)}
                className="mt-0.5"
              />
              <span className="text-gray-600">
                I agree to the Terms of Service
              </span>
            </label>
            <label className="flex items-start gap-2 text-sm">
              <input
                type="checkbox"
                checked={privacyConsent}
                onChange={(e) => setPrivacyConsent(e.target.checked)}
                className="mt-0.5"
              />
              <span className="text-gray-600">
                I consent to the Privacy Policy and data processing
              </span>
            </label>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-red-600 hover:bg-red-700 text-white py-2.5 rounded font-medium text-sm disabled:opacity-50"
          >
            {loading ? 'Creating account...' : 'Register'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-4">
          Already have an account?{' '}
          <Link href="/auth/login" className="text-red-600 hover:text-red-700">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
}
