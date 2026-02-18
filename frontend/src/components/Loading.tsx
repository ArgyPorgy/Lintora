import Ballpit from './Ballpit'

export default function Loading() {
  return (
    <div className="min-h-screen relative flex items-center justify-center">
      {/* Ballpit Background */}
      <div className="fixed inset-0 z-0" style={{ minHeight: '100vh', maxHeight: '100vh' }}>
        <Ballpit
          count={100}
          gravity={0.5}
          friction={0.9975}
          wallBounce={0.95}
          followCursor={true}
          colors={[0x4f46e5, 0x7c3aed, 0x10b981]}
        />
      </div>

      {/* Loading Content */}
      <div className="relative z-10 text-center">
        <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-indigo-600 border-t-transparent mb-6"></div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Loading Lintora</h2>
        <p className="text-gray-500">Preparing your security auditor...</p>
      </div>
    </div>
  )
}
