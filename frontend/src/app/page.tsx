export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8 bg-gray-50">
      <div className="max-w-md w-full text-center space-y-6">
        <h1 className="text-4xl font-bold text-gray-900">
          Welcome to SYRA
        </h1>
        <p className="text-lg text-gray-600">
          Medical Emergency Identification System
        </p>
        <div className="py-8">
          <div className="bg-white rounded-lg shadow-md p-8">
            <p className="text-gray-500">
              Your medical profile dashboard will appear here.
            </p>
          </div>
        </div>
        <div className="flex gap-4 justify-center">
          <a
            href="/login"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Login
          </a>
          <a
            href="/register"
            className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Register
          </a>
        </div>
      </div>
    </main>
  );
}
