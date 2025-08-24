import { requireAuth } from "@/lib/auth"
import { Navbar } from "@/components/Navbar"

export default async function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  await requireAuth()

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1a012b] via-[#2d0a4a] to-[#1a012b]">
      <Navbar />
      <main className="flex-1">{children}</main>
    </div>
  )
}
