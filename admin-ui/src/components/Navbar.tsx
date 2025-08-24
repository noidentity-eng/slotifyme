"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import {
  CreditCard,
  Users,
  Settings,
  Building2,
  Home,
  LogOut,
  Bell,
  Search,
} from "lucide-react"
import { Button } from "@/lib/ui"

const navigation = [
  { name: "Dashboard", href: "/admin/home", icon: Home },
  { name: "Plans & Add-ons", href: "/admin/plans", icon: CreditCard },
  { name: "Tenants", href: "/admin/tenants", icon: Building2 },
]

export function Navbar() {
  const pathname = usePathname()

  const handleLogout = async () => {
    try {
      await fetch("/logout", { method: "POST" })
      window.location.href = "/login"
    } catch (error) {
      console.error("Logout failed:", error)
    }
  }

  return (
    <nav className="bg-white/5 backdrop-blur-sm border-b border-white/10 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 premium-gradient rounded-lg flex items-center justify-center">
              <img src="/logo.svg" alt="Slotifyme Logo" className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Slotifyme</h1>
              <p className="text-xs text-gray-400">Admin Panel</p>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-1">
            {navigation.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-all duration-300",
                    isActive
                      ? "bg-gradient-to-r from-[#b17a50] to-[#d4a574] text-white shadow-lg"
                      : "text-gray-300 hover:bg-white/10 hover:text-white"
                  )}
                >
                  <item.icon
                    className={cn(
                      "mr-2 h-4 w-4",
                      isActive ? "text-white" : "text-gray-400"
                    )}
                  />
                  {item.name}
                </Link>
              )
            })}
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center space-x-4">
            {/* Search */}
            <div className="relative hidden sm:block">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-4 w-4 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Search..."
                className="bg-white/10 border border-white/20 text-white placeholder-gray-400 rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#b17a50] focus:border-transparent"
              />
            </div>

            {/* Notifications */}
            <Button
              variant="ghost"
              size="sm"
              className="relative text-gray-300 hover:text-white hover:bg-white/10"
            >
              <Bell className="h-5 w-5" />
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
            </Button>

            {/* User Menu */}
            <div className="flex items-center space-x-3">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium text-white">Arun</p>
                <p className="text-xs text-gray-400">arun@slotifyme.com</p>
              </div>
              <div className="w-8 h-8 premium-gradient rounded-full flex items-center justify-center">
                <span className="text-white font-semibold text-sm">A</span>
              </div>
            </div>

            {/* Logout Button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="text-gray-300 hover:text-white hover:bg-white/10"
            >
              <LogOut className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <div className="md:hidden">
        <div className="px-2 pt-2 pb-3 space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center px-3 py-2 text-base font-medium rounded-lg transition-all duration-300",
                  isActive
                    ? "bg-gradient-to-r from-[#b17a50] to-[#d4a574] text-white shadow-lg"
                    : "text-gray-300 hover:bg-white/10 hover:text-white"
                )}
              >
                <item.icon
                  className={cn(
                    "mr-3 h-5 w-5",
                    isActive ? "text-white" : "text-gray-400"
                  )}
                />
                {item.name}
              </Link>
            )
          })}
        </div>
      </div>
    </nav>
  )
}
