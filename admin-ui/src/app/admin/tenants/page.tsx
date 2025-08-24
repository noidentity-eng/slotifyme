"use client"

import { useState } from "react"
import { TenantTable } from "@/components/TenantTable"
import { NewTenantDrawer } from "@/components/NewTenantDrawer"
import { BootstrapButton } from "@/components/BootstrapButton"
import { Button } from "@/lib/ui"
import { Plus } from "lucide-react"

export default function TenantsPage() {
  const [isNewTenantOpen, setIsNewTenantOpen] = useState(false)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tenants</h1>
          <p className="text-gray-600">Manage tenant accounts and locations</p>
        </div>
        <div className="flex space-x-3">
          <BootstrapButton />
          <Button onClick={() => setIsNewTenantOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            New Tenant
          </Button>
        </div>
      </div>

      <TenantTable />

      <NewTenantDrawer
        open={isNewTenantOpen}
        onOpenChange={setIsNewTenantOpen}
      />
    </div>
  )
}

