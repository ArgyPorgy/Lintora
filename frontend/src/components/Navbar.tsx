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

export default function Navbar({ currentPage = 'home' }: NavbarProps) {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Use relative path - Vite proxy will route to backend
  const navItems: NavItem[] = [
    { id: 'home', label: 'Home', href: '/' },
    { id: 'developers', label: 'Developers', href: '/docs', external: true },
    { id: 'api', label: 'API', href: '/docs', external: true },
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
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <a href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <img src={logo} alt="Lintora" className="h-16 w-auto" />
          </a>

          {/* Navigation Items */}
          <div className="flex items-center gap-4">
            {navItems.map((item) => (
              <a
                key={item.id}
                href={item.href}
                target={item.external ? '_blank' : undefined}
                rel={item.external ? 'noopener noreferrer' : undefined}
                className={`
                  px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
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
            
            {/* Eigen Logo */}
            <div className="flex items-center">
              <img src={eigen} alt="Eigen" className="h-14 w-auto opacity-80 hover:opacity-100 transition-opacity" />
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}
