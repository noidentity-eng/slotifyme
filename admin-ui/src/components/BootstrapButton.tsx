"use client"

import { useMutation, useQueryClient } from "@tanstack/react-query"
import { apiPost, apiEndpoints } from "@/lib/fetcher"
import { Button } from "@/lib/ui"
import { useToast } from "@/components/Toast"
import { Sparkles } from "lucide-react"

export function BootstrapButton() {
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const bootstrapMutation = useMutation({
    mutationFn: () => apiPost(apiEndpoints.bootstrap.sampleTenants),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tenants"] })
      toast({
        title: "Success",
        description: "Sample tenants created successfully!",
      })
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to create sample tenants",
        variant: "destructive",
      })
    },
  })

  return (
    <Button
      variant="outline"
      onClick={() => bootstrapMutation.mutate()}
      disabled={bootstrapMutation.isPending}
    >
      <Sparkles className="h-4 w-4 mr-2" />
      {bootstrapMutation.isPending ? "Creating..." : "Bootstrap Sample Tenants"}
    </Button>
  )
}

