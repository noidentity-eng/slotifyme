"use client"
import { useEffect } from "react"

export default function DebugHelper() {
  if (process.env.NODE_ENV !== "development") return null

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      const el = document.elementFromPoint(e.clientX, e.clientY)
      // eslint-disable-next-line no-console
      console.log("[DebugHelper] Top element at click:", el)
    }
    window.addEventListener("click", handler, { capture: true })
    return () =>
      window.removeEventListener("click", handler, { capture: true } as any)
  }, [])

  return null
}
