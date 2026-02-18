import { useState, useEffect } from 'react'
import logo from '../logo.png'
import eigen from '../eigen.png'

interface NavItem {
  id: string
  label: string
  href: string
  external?: boolean
}

interface NavbarProps {
  currentPage?: 'home' | 'developers' | 'api'
}

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

export default function Navbar({ currentPage = 'home' }: NavbarProps) {
  const [scrolled, setScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Close mobile menu when clicking outside
  useEffect(() => {
    if (mobileMenuOpen) {
      const handleClickOutside = () => setMobileMenuOpen(false)
      document.addEventListener('click', handleClickOutside)
      return () => document.removeEventListener('click', handleClickOutside)
    }
  }, [mobileMenuOpen])

  // Use API URL for docs links
  const navItems: NavItem[] = [
    { id: 'home', label: 'Home', href: '/' },
    { id: 'developers', label: 'Developers', href: getApiUrl('/docs'), external: true },
    { id: 'api', label: 'API', href: getApiUrl('/docs'), external: true },
  ]

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-[100] transition-all duration-300 ${
        scrolled
          ? 'backdrop-blur-xl shadow-lg border-b border-gray-800'
          : 'backdrop-blur-sm'
      }`}
      style={{ 
        backgroundColor: 'rgba(0, 0, 0, 1)',
        isolation: 'isolate'
      }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14 sm:h-16">
          {/* Logo */}
          <a href="/" className="flex items-center gap-2 sm:gap-3 hover:opacity-80 transition-opacity">
            <img src={logo} alt="Lintora" className="h-10 sm:h-14 md:h-16 w-auto" />
          </a>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-4">
            {navItems.map((item) => (
              <a
                key={item.id}
                href={item.href}
                target={item.external ? '_blank' : undefined}
                rel={item.external ? 'noopener noreferrer' : undefined}
                className={`
                  px-3 sm:px-4 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all duration-200
                  ${
                    currentPage === item.id
                      ? 'bg-blue-700 text-white shadow-lg shadow-blue-500/30'
                      : item.external
                      ? 'text-white hover:text-blue-400 hover:bg-blue-900/30 hover:shadow-md hover:shadow-blue-500/20 border border-transparent hover:border-blue-500/50'
                      : scrolled
                      ? 'text-gray-300 hover:text-white hover:bg-gray-800'
                      : 'text-gray-300 hover:text-white hover:bg-white/10'
                  }
                `}
              >
                {item.label}
              </a>
            ))}
            
            {/* Eigen Logo - Desktop */}
            <div className="flex items-center ml-2">
              <img src={eigen} alt="Eigen" className="h-10 sm:h-12 md:h-14 w-auto opacity-80 hover:opacity-100 transition-opacity" />
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center gap-2">
            <button
              onClick={(e) => {
                e.stopPropagation()
                setMobileMenuOpen(!mobileMenuOpen)
              }}
              className="p-2 text-white hover:bg-gray-800 rounded-lg transition-colors"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div 
            className="md:hidden border-t border-gray-800 py-4 space-y-2"
            onClick={(e) => e.stopPropagation()}
          >
            {navItems.map((item) => (
              <a
                key={item.id}
                href={item.href}
                target={item.external ? '_blank' : undefined}
                rel={item.external ? 'noopener noreferrer' : undefined}
                onClick={() => setMobileMenuOpen(false)}
                className={`
                  block px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200
                  ${
                    currentPage === item.id
                      ? 'bg-blue-700 text-white'
                      : 'text-gray-300 hover:text-white hover:bg-gray-800'
                  }
                `}
              >
                {item.label}
              </a>
            ))}
            <div className="pt-2 border-t border-gray-800">
              <img src={eigen} alt="Eigen" className="h-10 w-auto opacity-80" />
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
