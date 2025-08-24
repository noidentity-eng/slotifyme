"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { CreditCard, Users, Settings, Building2, Home } from "lucide-react"

const navigation = [
  { name: "Dashboard", href: "/admin/home", icon: Home },
  { name: "Plans & Add-ons", href: "/admin/plans", icon: CreditCard },
  { name: "Tenants", href: "/admin/tenants", icon: Building2 },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="flex flex-col w-64 bg-white/5 backdrop-blur-sm border-r border-white/10 shadow-2xl">
      <div className="flex items-center h-16 px-6 border-b border-white/10">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 premium-gradient rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">S</span>
          </div>
          <h2 className="text-lg font-bold text-white">Slotifyme</h2>
        </div>
      </div>
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-all duration-300",
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
      </nav>

      {/* Premium Footer */}
      <div className="p-4 border-t border-white/10">
        <div className="text-center">
          <div className="w-8 h-1 premium-gradient rounded-full mx-auto mb-2"></div>
          <p className="text-xs text-gray-400">Premium Admin Panel</p>
        </div>
      </div>
    </div>
  )
}
