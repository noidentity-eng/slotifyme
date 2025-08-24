import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { QueryProvider } from "@/components/QueryProvider"
import { ToastProvider, ToastViewport } from "@/components/Toast"
import DebugHelper from "@/components/DebugHelper"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Slotifyme Admin",
  description: "Admin interface for Slotifyme",
  // PWA/App Icon Configuration - DISABLED
  // To re-enable PWA install support, uncomment and configure these:
  // manifest: "/manifest.json",
  // appleWebApp: {
  //   capable: true,
  //   statusBarStyle: "default",
  //   title: "Slotifyme Admin",
  // },
  // icons: {
  //   icon: [
  //     { url: "/favicon-16x16.png", sizes: "16x16", type: "image/png" },
  //     { url: "/favicon-32x32.png", sizes: "32x32", type: "image/png" },
  //   ],
  //   apple: [
  //     { url: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" },
  //   ],
  //   other: [
  //     { rel: "mask-icon", url: "/safari-pinned-tab.svg", color: "#1a012b" },
  //   ],
  // },
  // Only include basic favicon - no PWA features
  // Note: Add your favicon.ico file to the public/ directory
  // icons: {
  //   icon: "/favicon.ico",
  // },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <QueryProvider>
          <ToastProvider>
            {children}
            <ToastViewport />
            <DebugHelper />
          </ToastProvider>
        </QueryProvider>
      </body>
    </html>
  )
}
