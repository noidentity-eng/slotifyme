"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiGet, apiPut, apiEndpoints } from "@/lib/fetcher"
import { type Addon } from "@/lib/zod-schemas"
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
  Button,
  Input,
} from "@/lib/ui"
import { formatPrice } from "@/lib/utils"
import { useToast } from "@/components/Toast"
import { Edit, Save, X } from "lucide-react"

export function AddonTable() {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [editingAddon, setEditingAddon] = useState<string | null>(null)
  const [editData, setEditData] = useState<{ pricing_ref?: string }>({})

  const { data: addons = [], isLoading } = useQuery({
    queryKey: ["addons"],
    queryFn: () => apiGet<Addon[]>(apiEndpoints.admin.addons),
  })

  const updateAddonMutation = useMutation({
    mutationFn: ({
      code,
      data,
    }: {
      code: string
      data: { pricing_ref?: string }
    }) => apiPut(apiEndpoints.admin.addon(code), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["addons"] })
      setEditingAddon(null)
      setEditData({})
      toast({
        title: "Success",
        description: "Addon updated successfully",
      })
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to update addon",
        variant: "destructive",
      })
    },
  })

  const handleEdit = (addon: Addon) => {
    setEditingAddon(addon.code)
    setEditData({
      pricing_ref: addon.pricing_ref,
    })
  }

  const handleSave = (code: string) => {
    updateAddonMutation.mutate({ code, data: editData })
  }

  const handleCancel = () => {
    setEditingAddon(null)
    setEditData({})
  }

  const renderEffectChips = (effect: Record<string, boolean>) => {
    return Object.entries(effect).map(([feature, enabled]) => (
      <span
        key={feature}
        className={`inline-block px-3 py-1 text-xs rounded-full mr-2 mb-2 font-medium ${
          enabled
            ? "bg-gradient-to-r from-[#b17a50] to-[#d4a574] text-white shadow-lg"
            : "bg-white/10 text-gray-400 border border-white/20"
        }`}
      >
        {feature.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
      </span>
    ))
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="w-12 h-12 premium-gradient rounded-full mx-auto mb-4 animate-spin"></div>
          <p className="text-gray-400 text-lg">Loading premium add-ons...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="overflow-hidden rounded-xl border border-white/10 bg-white/5">
        <Table>
          <TableHeader>
            <TableRow className="border-white/10 bg-white/5">
              <TableHead className="text-[#b17a50] font-semibold">
                Code
              </TableHead>
              <TableHead className="text-[#b17a50] font-semibold">
                Description
              </TableHead>
              <TableHead className="text-[#b17a50] font-semibold">
                Preview Price
              </TableHead>
              <TableHead className="text-[#b17a50] font-semibold">
                Pricing Ref
              </TableHead>
              <TableHead className="text-[#b17a50] font-semibold">
                Actions
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {addons.map((addon) => (
              <TableRow
                key={addon.code}
                className="border-white/10 hover:bg-white/5 transition-colors"
              >
                <TableCell>
                  <div>
                    <div className="font-semibold text-white">{addon.name}</div>
                    <div className="text-sm text-[#b17a50] font-medium">
                      {addon.code}
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="max-w-xs">
                    {renderEffectChips(addon.effect)}
                  </div>
                </TableCell>
                <TableCell>
                  <span className="text-[#b17a50] font-bold text-lg">
                    {addon.preview_amount_cents
                      ? formatPrice(addon.preview_amount_cents)
                      : "N/A"}
                  </span>
                </TableCell>
                <TableCell>
                  {editingAddon === addon.code ? (
                    <Input
                      className="bg-white/10 border-white/20 text-white placeholder-gray-400"
                      value={editData.pricing_ref || addon.pricing_ref || ""}
                      onChange={(e) =>
                        setEditData({
                          ...editData,
                          pricing_ref: e.target.value,
                        })
                      }
                      placeholder="Enter pricing reference"
                    />
                  ) : (
                    <span className="text-gray-300">
                      {addon.pricing_ref || "N/A"}
                    </span>
                  )}
                </TableCell>
                <TableCell>
                  {editingAddon === addon.code ? (
                    <div className="flex space-x-2">
                      <Button
                        size="sm"
                        className="premium-button"
                        onClick={() => handleSave(addon.code)}
                        disabled={updateAddonMutation.isPending}
                      >
                        <Save className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        className="premium-button-outline"
                        onClick={handleCancel}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ) : (
                    <Button
                      size="sm"
                      className="premium-button-outline"
                      onClick={() => handleEdit(addon)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
