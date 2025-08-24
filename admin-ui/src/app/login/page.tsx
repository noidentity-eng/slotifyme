"use client"

import React, { useState } from "react"
import { useRouter } from "next/navigation"
import { apiPost, apiEndpoints } from "@/lib/fetcher"
import { useToast } from "@/components/Toast"
import { Eye, EyeOff, Mail, Lock, LogIn } from "lucide-react"

type AuthState =
  | "login"
  | "forgot-password"
  | "security-questions"
  | "reset-password"

export default function LoginPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [authState, setAuthState] = useState<AuthState>("login")
  const [userEmail, setUserEmail] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [errors, setErrors] = useState<{ [key: string]: string }>({})
  const [isLoading, setIsLoading] = useState(false)

  const validateForm = (formData: { email: string; password: string }) => {
    const newErrors: { [key: string]: string } = {}

    if (!formData.email) {
      newErrors.email = "Email is required"
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Please enter a valid email address"
    }

    if (!formData.password) {
      newErrors.password = "Password is required"
    } else if (formData.password.length < 6) {
      newErrors.password = "Password must be at least 6 characters"
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    const formData = new FormData(e.currentTarget)
    const email = formData.get("email") as string
    const password = formData.get("password") as string

    const data = { email, password }

    if (!validateForm(data)) return

    setIsLoading(true)

    try {
      await apiPost(apiEndpoints.auth.login, data)
      router.push("/admin")
      toast({
        title: "Success",
        description: "Logged in successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Login failed. Please check your credentials.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleForgotPassword = () => {
    setAuthState("forgot-password")
  }

  const LoginForm = () => (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Email Field - Simplified */}
      <div className="space-y-2">
        <label
          htmlFor="email"
          className="block text-sm font-semibold text-gray-700"
        >
          Email Address
        </label>
        <input
          type="email"
          id="email"
          name="email"
          className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-amber-500 bg-white text-gray-900"
          placeholder="Enter your email"
          style={{ zIndex: 9999, position: "relative" }}
        />
      </div>

      {/* Password Field - Simplified */}
      <div className="space-y-2">
        <label
          htmlFor="password"
          className="block text-sm font-semibold text-gray-700"
        >
          Password
        </label>
        <input
          type="password"
          id="password"
          name="password"
          className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-amber-500 bg-white text-gray-900"
          placeholder="Enter your password"
          style={{ zIndex: 9999, position: "relative" }}
        />
      </div>

      {/* Forgot Password Link */}
      <div className="flex justify-end">
        <button
          type="button"
          onClick={handleForgotPassword}
          className="text-sm font-medium text-amber-600 hover:text-amber-700 transition-colors duration-200"
        >
          Forgot your password?
        </button>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-gradient-to-r from-amber-500 to-amber-600 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 hover:from-amber-600 hover:to-amber-700 focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:ring-offset-2 disabled:opacity-70 disabled:cursor-not-allowed transform hover:scale-[1.02] active:scale-[0.98]"
      >
        <div className="flex items-center justify-center space-x-2">
          {isLoading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Signing in...</span>
            </>
          ) : (
            <>
              <LogIn className="w-5 h-5" />
              <span>Sign In to Dashboard</span>
            </>
          )}
        </div>
      </button>

      {/* Additional Options */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <p className="text-center text-sm text-gray-600">
          Need help accessing your account?{" "}
          <button
            type="button"
            onClick={handleForgotPassword}
            className="font-medium text-amber-600 hover:text-amber-700 transition-colors"
          >
            Account Recovery
          </button>
        </p>
      </div>
    </form>
  )

  return (
    <div className="min-h-screen w-full bg-[#1a012b] flex items-center justify-center p-4 sm:p-6 lg:p-8 relative">
      <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width=%22100%22 height=%22100%22 viewBox=%220 0 100 100%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cdefs%3E%3Cpattern id=%22darkTexture%22 x=%220%22 y=%220%22 width=%2250%22 height=%2250%22 patternUnits=%22userSpaceOnUse%22%3E%3Cpath d=%22M0 0h50v50H0z%22 fill=%22%230f172a%22/%3E%3Cpath d=%22M25 0c13.807 0 25 11.193 25 25s-11.193 25-25 25S0 38.807 0 25 11.193 0 25 0z%22 fill=%22%23172554%22 fill-opacity=%220.4%22/%3E%3Cpath d=%22M12.5 12.5c6.904 0 12.5 5.596 12.5 12.5s-5.596 12.5-12.5 12.5S0 31.904 0 25s5.596-12.5 12.5-12.5z%22 fill=%22%231e293b%22 fill-opacity=%220.6%22/%3E%3Cpath d=%22M37.5 37.5c6.904 0 12.5 5.596 12.5 12.5s-5.596 12.5-12.5 12.5S25 56.904 25 50s5.596-12.5 12.5-12.5z%22 fill=%22%231e293b%22 fill-opacity=%220.6%22/%3E%3Cpath d=%22M6 6l4 4-4 4-4-4z%22 fill=%22%23334155%22 fill-opacity=%220.3%22/%3E%3Cpath d=%22M44 44l4 4-4 4-4-4z%22 fill=%22%23334155%22 fill-opacity=%220.3%22/%3E%3Cpath d=%22M19 6l4 4-4 4-4-4z%22 fill=%22%23334155%22 fill-opacity=%220.2%22/%3E%3Cpath d=%22M31 44l4 4-4 4-4-4z%22 fill=%22%23334155%22 fill-opacity=%220.2%22/%3E%3C/pattern%3E%3C/defs%3E%3Crect width=%22100%25%22 height=%22100%25%22 fill=%22url(%23darkTexture)%22/%3E%3C/svg%3E')] opacity-80 -z-10 pointer-events-none"></div>
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900/30 via-blue-950/20 to-slate-900/30 -z-10 pointer-events-none"></div>

      <div className="w-full max-w-md mx-auto relative z-10">
        <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl p-6 sm:p-8 transition-all duration-500 hover:shadow-3xl border border-slate-200/20">
          {/* Header */}
          <div className="text-center mb-6 sm:mb-8">
            <div className="mb-4">
              <div className="w-[400px] h-[75px] rounded-2xl overflow-hidden">
                <img
                  src="/logo.svg"
                  alt="Slotifyme Logo"
                  className="w-full h-full object-contain"
                />
              </div>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
              Slotifyme Admin
            </h1>
            <p className="text-sm sm:text-base text-gray-600 font-medium">
              {authState === "login" && "Welcome back to your dashboard"}
              {authState === "forgot-password" && "Reset your password"}
              {authState === "security-questions" && "Verify your identity"}
              {authState === "reset-password" && "Create new password"}
            </p>
          </div>

          {/* Auth Component */}
          <div className="transition-all duration-300 ease-in-out">
            <LoginForm />
          </div>

          {/* Footer */}
          <div className="mt-6 sm:mt-8 pt-4 sm:pt-6 border-t border-gray-200">
            <p className="text-center text-xs sm:text-sm text-gray-500">
              © 2025 Slotifyme Admin. Secure & Professional.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
