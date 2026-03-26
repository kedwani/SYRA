import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-[calc(100vh-57px)] flex flex-col items-center justify-center px-4">
      <div className="text-center max-w-xl">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          SYRA
        </h1>
        <p className="text-lg text-gray-600 mb-2">
          Medical Emergency Platform
        </p>
        <p className="text-sm text-gray-500 mb-8">
          Store your medical information securely. Share it instantly via QR code in emergencies.
        </p>

        <div className="flex gap-4 justify-center">
          <Link
            href="/auth/login"
            className="bg-red-600 hover:bg-red-700 text-white px-6 py-2.5 rounded-lg font-medium text-sm"
          >
            Login
          </Link>
          <Link
            href="/auth/register"
            className="bg-white hover:bg-gray-50 text-gray-900 border border-gray-300 px-6 py-2.5 rounded-lg font-medium text-sm"
          >
            Register
          </Link>
        </div>

        <div className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-6 text-left">
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-sm mb-1">Medical Profile</h3>
            <p className="text-xs text-gray-500">
              Store allergies, medications, and conditions securely.
            </p>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-sm mb-1">QR Access</h3>
            <p className="text-xs text-gray-500">
              First responders can scan your bracelet to access critical info.
            </p>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-sm mb-1">Emergency Ready</h3>
            <p className="text-xs text-gray-500">
              Large, high-contrast emergency page loads instantly.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
