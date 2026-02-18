import { useState, useRef, useCallback, useEffect } from 'react'
import Ballpit from './components/Ballpit'
import Navbar from './components/Navbar'

type JobStatus = 'idle' | 'uploading' | 'processing' | 'completed' | 'failed'

// Get API base URL - use environment variable in production, relative path in dev
const getApiUrl = (path: string): string => {
  const apiBase = import.meta.env.VITE_API_URL || ''
  // If VITE_API_URL is set, use it (production)
  if (apiBase) {
    // Remove trailing slash from apiBase if present
    const base = apiBase.replace(/\/$/, '')
    return `${base}${path}`
  }
  // Otherwise use relative path (development with Vite proxy)
  return path
}

function App() {
  const [file, setFile] = useState<File | null>(null)
  const [projectName, setProjectName] = useState('')
  const [status, setStatus] = useState<JobStatus>('idle')
  const [jobId, setJobId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isMobile, setIsMobile] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Detect mobile screen size
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 640)
    }
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile?.name.endsWith('.zip')) {
      setFile(droppedFile)
      setProjectName(droppedFile.name.replace('.zip', ''))
      setError(null)
    } else {
      setError('Please upload a ZIP file')
    }
  }, [])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile?.name.endsWith('.zip')) {
      setFile(selectedFile)
      setProjectName(selectedFile.name.replace('.zip', ''))
      setError(null)
    } else {
      setError('Please upload a ZIP file')
    }
  }

  const pollJobStatus = async (id: string) => {
    const interval = setInterval(async () => {
      try {
        const url = getApiUrl(`/audit/${id}`)
        const response = await fetch(url)
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }
        
        const data = await response.json()
        
        if (data.status === 'completed') {
          clearInterval(interval)
          setStatus('completed')
          setJobId(id)
        } else if (data.status === 'failed') {
          clearInterval(interval)
          setStatus('failed')
          setError(data.error || 'Analysis failed')
        }
      } catch {
        clearInterval(interval)
        setStatus('failed')
        setError('Failed to check status')
      }
    }, 2000)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) {
      setError('Please select a ZIP file')
      return
    }

    setStatus('uploading')
    setError(null)

    const formData = new FormData()
    formData.append('file', file)
    formData.append('project_name', projectName || file.name.replace('.zip', ''))

    try {
      const url = getApiUrl('/audit')
      console.log('Uploading to:', url) // Debug log
      
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
          // Don't set Content-Type, let browser set it with boundary for FormData
        }
      })

      if (!response.ok) {
        let errorMessage = 'Upload failed'
        try {
          const contentType = response.headers.get('content-type')
          if (contentType && contentType.includes('application/json')) {
            const data = await response.json()
            errorMessage = data.detail || data.message || errorMessage
          } else {
            const text = await response.text()
            errorMessage = text || `HTTP ${response.status}: ${response.statusText}`
          }
        } catch {
          errorMessage = `HTTP ${response.status}: ${response.statusText}`
        }
        throw new Error(errorMessage)
      }

      // Check content type before parsing
      const contentType = response.headers.get('content-type')
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text()
        throw new Error(`Unexpected response format. Expected JSON, got: ${contentType || 'unknown'}. Response: ${text.substring(0, 100)}`)
      }

      // Get response text first
      const text = await response.text()
      if (!text || text.trim() === '') {
        throw new Error('Empty response from server')
      }

      // Parse JSON
      let data
      try {
        data = JSON.parse(text)
      } catch (parseErr) {
        throw new Error(`Invalid JSON response: ${parseErr instanceof Error ? parseErr.message : 'Unknown error'}. Response: ${text.substring(0, 200)}`)
      }

      if (!data.job_id) {
        throw new Error('Response missing job_id field')
      }

      setStatus('processing')
      pollJobStatus(data.job_id)
    } catch (err) {
      setStatus('failed')
      const errorMsg = err instanceof Error ? err.message : 'An error occurred'
      console.error('Upload error:', err) // Debug log
      setError(errorMsg)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="min-h-screen relative">
      {/* Navbar */}
      <Navbar currentPage="home" />

      {/* Ballpit Background */}
      <div 
        className="fixed inset-0 z-0" 
        style={{ 
          minHeight: '100vh', 
          maxHeight: '100vh',
          clipPath: 'inset(56px 0 0 0)' // Clip top navbar height (56px on mobile, 64px on desktop)
        }}
      >
        <Ballpit
          count={isMobile ? 50 : 100}
          gravity={0.5}
          friction={0.9975}
          wallBounce={0.95}
          followCursor={true}
          colors={[0xff0000, 0xcc0000, 0x990000, 0x660000, 0x330000]}
        />
      </div>

      {/* Content */}
      <div className="relative z-10 min-h-screen flex flex-col items-center px-3 sm:px-4 pt-20 sm:pt-24 md:pt-32 pb-12 sm:pb-16 md:pb-24 pointer-events-auto">
        {/* Hero Section - Visible First */}
        <div className="w-full max-w-4xl text-center mb-12 sm:mb-16 md:mb-24 lg:mb-32">
          <div className="inline-flex items-center gap-1.5 sm:gap-2 bg-blue-900/30 text-blue-400 border border-blue-500/30 px-3 sm:px-4 py-1 sm:py-1.5 rounded-full text-xs sm:text-sm font-semibold mb-4 sm:mb-6">
            <span className="w-1 h-1 sm:w-1.5 sm:h-1.5 bg-blue-500 rounded-full animate-pulse"></span>
            Built with ❤️ by Arghya
          </div>
          <h1 className="font-display text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold text-white tracking-tight mb-4 sm:mb-6 px-2">
            <span className="bg-gradient-to-r from-blue-400 to-blue-600 bg-clip-text text-transparent">
              Private Security Agent
            </span>
            <br />for Smart Contracts
          </h1>
          <p className="text-gray-300 text-base sm:text-lg md:text-xl lg:text-2xl max-w-3xl mx-auto mb-4 px-2">
            Get comprehensive security audits powered by AI. your code stays private, never exposed to humans.
          </p>
        </div>

        {/* Upload Section - Appears on Scroll */}
        <div className="w-full max-w-2xl">

          {/* Main Card */}
          <div className="bg-white/10 backdrop-blur-xl rounded-2xl sm:rounded-3xl shadow-2xl shadow-blue-900/20 p-4 sm:p-6 md:p-8 border border-gray-800">
            <form onSubmit={handleSubmit}>
              {/* Upload Area */}
              <div
                className={`
                  border-2 border-dashed rounded-xl sm:rounded-2xl p-6 sm:p-8 md:p-12 text-center cursor-pointer transition-all touch-manipulation
                  ${file 
                    ? 'border-blue-500 bg-blue-900/20' 
                    : 'border-gray-700 hover:border-blue-500 hover:bg-blue-900/10 active:bg-blue-900/20'
                  }
                `}
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".zip"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                
                {file ? (
                  <div>
                    <p className="font-semibold text-white text-sm sm:text-base md:text-lg mb-1 sm:mb-2 break-words px-2">{file.name}</p>
                    <p className="text-xs sm:text-sm text-gray-400">{formatFileSize(file.size)}</p>
                  </div>
                ) : (
                  <>
                    <p className="font-semibold text-white text-sm sm:text-base md:text-lg mb-1 sm:mb-2 px-2">Drop your ZIP file here</p>
                    <p className="text-xs sm:text-sm text-gray-400 mb-2 px-2">or tap to browse • Only .sol files will be analyzed</p>
                    <p className="text-[10px] sm:text-xs text-gray-500 mt-3 pt-3 border-t border-gray-800 px-2 leading-relaxed">
                      🔐 Your code is processed in secure enclaves • Never accessed by humans • Cryptographically signed reports
                    </p>
                  </>
                )}
              </div>

              {/* Error Message */}
              {error && (
                <div className="mt-3 sm:mt-4 p-3 sm:p-4 bg-red-900/30 border border-red-500/50 rounded-lg sm:rounded-xl text-red-400 text-xs sm:text-sm break-words">
                  {error}
                </div>
              )}

              {/* Input */}
              <div className="mt-4 sm:mt-6 flex flex-col sm:flex-row gap-2 sm:gap-0 sm:relative">
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  placeholder="Audit this Solidity contract..."
                  className="w-full px-4 sm:px-5 py-3 sm:py-4 sm:pr-32 bg-gray-900/50 border-2 border-gray-700 rounded-xl sm:rounded-2xl text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-2 sm:focus:ring-4 focus:ring-blue-500/20 transition-all text-sm sm:text-base"
                />
                <button
                  type="submit"
                  disabled={status === 'uploading' || status === 'processing'}
                  className="w-full sm:w-auto sm:absolute sm:right-2 sm:top-1/2 sm:-translate-y-1/2 px-5 py-3 sm:py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-blue-500/50 hover:from-blue-500 hover:to-blue-600 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 text-sm sm:text-base touch-manipulation min-h-[44px]"
                >
                  {status === 'uploading' || status === 'processing' ? (
                    <>
                      <svg className="animate-spin h-4 w-4 sm:h-4 sm:w-4" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      <span className="hidden sm:inline">{status === 'uploading' ? 'Uploading...' : 'Analyzing...'}</span>
                      <span className="sm:hidden">{status === 'uploading' ? 'Uploading...' : 'Analyzing...'}</span>
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M5 12h14M12 5l7 7-7 7" />
                      </svg>
                      <span>Audit</span>
                    </>
                  )}
                </button>
              </div>
            </form>

          </div>

          {/* Result Card */}
          {status === 'completed' && jobId && (
            <div className="mt-4 sm:mt-6 bg-white/10 backdrop-blur-xl rounded-xl sm:rounded-2xl p-6 sm:p-8 text-center border border-blue-500/30 shadow-lg shadow-blue-900/20">
              <div className="text-3xl sm:text-4xl mb-3 sm:mb-4">✅</div>
              <h3 className="text-lg sm:text-xl font-bold text-white mb-2">Audit Complete!</h3>
              <p className="text-sm sm:text-base text-gray-300 mb-4 sm:mb-6">Your security report is ready to view.</p>
              <a
                href={getApiUrl(`/report/${jobId}`)}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 px-5 sm:px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-blue-500/50 hover:from-blue-500 hover:to-blue-600 active:scale-95 transition-all text-sm sm:text-base touch-manipulation min-h-[44px] w-full sm:w-auto"
              >
                View Report
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                  <polyline points="15 3 21 3 21 9" />
                  <line x1="10" y1="14" x2="21" y2="3" />
                </svg>
              </a>
            </div>
          )}

          {/* Footer */}
          
        </div>
      </div>
    </div>
  )
}

export default App
