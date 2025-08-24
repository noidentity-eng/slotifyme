"use client"

import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
// DevTools - DISABLED in production
// To re-enable devtools, uncomment the import and the JSX below
// import { ReactQueryDevtools } from "@tanstack/react-query-devtools"
import { useState } from "react"

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            retry: 1,
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {/* DevTools - DISABLED in production */}
      {/* To re-enable devtools, uncomment the import above and this JSX: */}
      {/* {process.env.NODE_ENV === 'development' && <ReactQueryDevtools initialIsOpen={false} />} */}
    </QueryClientProvider>
  )
}
