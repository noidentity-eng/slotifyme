"use client"

import { PlanTable } from "@/components/PlanTable"
import { AddonTable } from "@/components/AddonTable"
import { Card, CardHeader, CardTitle, CardContent } from "@/lib/ui"

export default function PlansPage() {
  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Premium Header */}
        <div className="text-center mb-12">
          <div className="inline-block p-2 mb-4">
            <div className="w-16 h-1 premium-gradient rounded-full mx-auto"></div>
          </div>
          <h1 className="text-5xl font-bold text-white mb-4 tracking-tight">
            Plans & <span className="premium-text">Add-ons</span>
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Manage subscription plans and premium add-on features with our
            enterprise-grade platform
          </p>
        </div>

        {/* Plans Section */}
        <div className="premium-card p-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">
                Subscription Plans
              </h2>
              <p className="text-gray-400">
                Choose the perfect plan for your business needs
              </p>
            </div>
            <div className="w-12 h-12 premium-gradient rounded-full flex items-center justify-center">
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
          </div>
          <PlanTable />
        </div>

        {/* Add-ons Section */}
        <div className="premium-card p-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">
                Premium Add-ons
              </h2>
              <p className="text-gray-400">
                Enhance your experience with powerful add-ons
              </p>
            </div>
            <div className="w-12 h-12 premium-gradient rounded-full flex items-center justify-center">
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
          </div>
          <AddonTable />
        </div>
      </div>
    </div>
  )
}
