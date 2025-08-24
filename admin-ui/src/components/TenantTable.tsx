"use client"

import { useQuery } from "@tanstack/react-query"
import { apiGet, apiEndpoints } from "@/lib/fetcher"
import { type TenantsResponse } from "@/lib/zod-schemas"
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/lib/ui"
import { formatDate } from "@/lib/utils"

export function TenantTable() {
  const { data: tenantsResponse, isLoading } = useQuery({
    queryKey: ["tenants"],
    queryFn: () => apiGet<TenantsResponse>(apiEndpoints.admin.tenants),
  })

  if (isLoading) {
    return <div>Loading tenants...</div>
  }

  const tenants = tenantsResponse?.items || []

  return (
    <Card>
      <CardHeader>
        <CardTitle>All Tenants</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Slug</TableHead>
              <TableHead>Locations Count</TableHead>
              <TableHead>Plan</TableHead>
              <TableHead>Created</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {tenants.map((tenant) => (
              <TableRow key={tenant.tenant_id}>
                <TableCell>
                  <div className="font-medium">{tenant.name}</div>
                </TableCell>
                <TableCell>
                  <code className="text-sm bg-gray-100 px-2 py-1 rounded">
                    {tenant.slug}
                  </code>
                </TableCell>
                <TableCell>{tenant.locations_count}</TableCell>
                <TableCell>
                  {tenant.plan ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {tenant.plan}
                    </span>
                  ) : (
                    <span className="text-gray-500">No plan</span>
                  )}
                </TableCell>
                <TableCell>
                  {tenant.tenant_id ? formatDate(new Date()) : "N/A"}
                </TableCell>
                <TableCell>
                  <div className="text-sm text-gray-500">View details</div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        {tenants.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No tenants found. Create your first tenant or bootstrap sample data.
          </div>
        )}
      </CardContent>
    </Card>
  )
}

