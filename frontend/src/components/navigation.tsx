'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { BookOpen, Users, RotateCw, AlertTriangle } from 'lucide-react'
import clsx from 'clsx'

export default function Navigation() {
  const pathname = usePathname()

  const links = [
    { href: '/', label: 'Dashboard', icon: BookOpen },
    { href: '/members', label: 'Members', icon: Users },
    { href: '/books', label: 'Books', icon: BookOpen },
    { href: '/borrowings', label: 'Borrowings', icon: RotateCw },
    { href: '/fines', label: 'Fines', icon: AlertTriangle },
  ]

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 justify-between items-center">
          <div className="flex items-center gap-8">
            <Link href="/" className="flex items-center gap-2 font-bold text-xl text-primary-600">
              <BookOpen className="w-6 h-6" />
              Library
            </Link>
            <div className="hidden md:flex gap-1">
              {links.map((link) => {
                const Icon = link.icon
                const isActive = pathname === link.href
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={clsx(
                      'px-3 py-2 rounded-md text-sm font-medium flex items-center gap-2 transition-colors',
                      isActive
                        ? 'bg-primary-100 text-primary-700'
                        : 'text-gray-600 hover:bg-gray-100'
                    )}
                  >
                    <Icon className="w-4 h-4" />
                    {link.label}
                  </Link>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}
