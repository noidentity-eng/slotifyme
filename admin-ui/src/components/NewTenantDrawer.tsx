"use client"

import React, { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import * as Dialog from "@radix-ui/react-dialog"
import { newTenantSchema, type NewTenantFormData } from "@/lib/zod-schemas"
import { apiPost, apiEndpoints } from "@/lib/fetcher"
import { env } from "@/lib/env"
import {
  Button,
  Input,
  Label,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardFooter,
} from "@/lib/ui"
import { useToast } from "@/components/Toast"
import { X, Globe } from "lucide-react"

interface NewTenantDrawerProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const timezones = [
  "America/New_York",
  "America/Chicago",
  "America/Denver",
  "America/Los_Angeles",
  "America/Anchorage",
  "Pacific/Honolulu",
  "Europe/London",
  "Europe/Paris",
  "Asia/Tokyo",
  "Australia/Sydney",
]

const planOptions = [
  { value: "basic", label: "Basic Plan" },
  { value: "professional", label: "Professional Plan" },
  { value: "enterprise", label: "Enterprise Plan" },
]

const addonOptions = [
  { value: "ai_booking", label: "AI Booking" },
  { value: "variable_pricing", label: "Variable Pricing" },
  { value: "value_pack", label: "Value Pack" },
]

export function NewTenantDrawer({ open, onOpenChange }: NewTenantDrawerProps) {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [slugPreview, setSlugPreview] = useState("")

  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors, isValid, isSubmitting },
  } = useForm<NewTenantFormData>({
    resolver: zodResolver(newTenantSchema),
    mode: "onChange",
    reValidateMode: "onChange",
    defaultValues: {
      tenant: { name: "", slug: "" },
      location: {
        name: "",
        slug: "",
        timezone: "America/New_York",
        phone: "",
        phone_public: false,
      },
      plan: {
        code: "basic",
        addons: [],
        pricing_ref: "",
      },
    },
  })

  const watchedTenantSlug = watch("tenant.slug")
  const watchedLocationSlug = watch("location.slug")

  // Update slug preview when slugs change
  React.useEffect(() => {
    if (watchedTenantSlug && watchedLocationSlug) {
      setSlugPreview(`/${watchedTenantSlug}/${watchedLocationSlug}`)
    } else {
      setSlugPreview("")
    }
  }, [watchedTenantSlug, watchedLocationSlug])

  const createTenantMutation = useMutation({
    mutationFn: (data: NewTenantFormData) => {
      const payload = {
        ...data,
        slugs: [
          {
            host: env.PUBLIC_HOST_DOMAIN,
            path: `/${data.tenant.slug}/${data.location.slug}`,
          },
        ],
      }
      return apiPost(apiEndpoints.admin.tenants, payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tenants"] })
      reset()
      onOpenChange(false)
      toast({
        title: "Success",
        description: "Tenant created successfully",
      })
    },
    onError: (error) => {
      console.error("Error creating tenant:", error)
      toast({
        title: "Error",
        description: "Failed to create tenant",
        variant: "destructive",
      })
    },
  })

  const onSubmit = async (data: NewTenantFormData) => {
    console.log("[submit] create-tenant", data)
    createTenantMutation.mutate(data)
  }

  const handleClose = () => {
    reset()
    onOpenChange(false)
  }

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50 pointer-events-none" />
        <Dialog.Content className="fixed right-0 top-0 h-full w-full max-w-md bg-white shadow-xl z-50 flex flex-col pointer-events-auto">
          <div className="flex items-center justify-between p-6 border-b">
            <Dialog.Title className="text-lg font-semibold">
              New Tenant
            </Dialog.Title>
            <Dialog.Close asChild>
              <Button variant="ghost" size="sm" onClick={handleClose}>
                <X className="h-4 w-4" />
              </Button>
            </Dialog.Close>
          </div>

          <form
            onSubmit={handleSubmit(onSubmit)}
            noValidate
            className="flex-1 flex flex-col overflow-hidden"
          >
            <div className="flex-1 p-6 space-y-6 overflow-y-auto">
              {/* Tenant Information */}
              <div className="space-y-4">
                <h3 className="text-sm font-medium text-gray-900">
                  Tenant Information
                </h3>

                <div className="space-y-2">
                  <Label htmlFor="tenant-name">Tenant Name</Label>
                  <Input
                    id="tenant-name"
                    {...register("tenant.name", { required: true })}
                    placeholder="Enter tenant name"
                    required
                  />
                  {errors.tenant?.name && (
                    <p className="text-sm text-red-600">
                      {errors.tenant.name.message}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="tenant-slug">Tenant Slug</Label>
                  <Input
                    id="tenant-slug"
                    {...register("tenant.slug", { required: true })}
                    placeholder="tenant-slug"
                    required
                  />
                  {errors.tenant?.slug && (
                    <p className="text-sm text-red-600">
                      {errors.tenant.slug.message}
                    </p>
                  )}
                </div>
              </div>

              {/* Location Information */}
              <div className="space-y-4">
                <h3 className="text-sm font-medium text-gray-900">
                  First Location
                </h3>

                <div className="space-y-2">
                  <Label htmlFor="location-name">Location Name</Label>
                  <Input
                    id="location-name"
                    {...register("location.name", { required: true })}
                    placeholder="Enter location name"
                    required
                  />
                  {errors.location?.name && (
                    <p className="text-sm text-red-600">
                      {errors.location.name.message}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="location-slug">Location Slug</Label>
                  <Input
                    id="location-slug"
                    {...register("location.slug", { required: true })}
                    placeholder="location-slug"
                    required
                  />
                  {errors.location?.slug && (
                    <p className="text-sm text-red-600">
                      {errors.location.slug.message}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="timezone">Timezone</Label>
                  <select
                    id="timezone"
                    {...register("location.timezone", { required: true })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    {timezones.map((tz) => (
                      <option key={tz} value={tz}>
                        {tz}
                      </option>
                    ))}
                  </select>
                  {errors.location?.timezone && (
                    <p className="text-sm text-red-600">
                      {errors.location.timezone.message}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input
                    id="phone"
                    {...register("location.phone", { required: true })}
                    placeholder="+1 (555) 123-4567"
                    required
                  />
                  {errors.location?.phone && (
                    <p className="text-sm text-red-600">
                      {errors.location.phone.message}
                    </p>
                  )}
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="phone-public"
                    {...register("location.phone_public")}
                    className="rounded border-gray-300"
                  />
                  <Label htmlFor="phone-public">Make phone number public</Label>
                </div>
              </div>

              {/* Plan Selection */}
              <div className="space-y-4">
                <h3 className="text-sm font-medium text-gray-900">
                  Plan & Add-ons
                </h3>

                <div className="space-y-2">
                  <Label>Plan</Label>
                  <div className="space-y-2">
                    {planOptions.map((plan) => (
                      <div
                        key={plan.value}
                        className="flex items-center space-x-2"
                      >
                        <input
                          type="radio"
                          id={`plan-${plan.value}`}
                          value={plan.value}
                          {...register("plan.code")}
                          className="rounded border-gray-300"
                        />
                        <Label htmlFor={`plan-${plan.value}`}>
                          {plan.label}
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Add-ons</Label>
                  <div className="space-y-2">
                    {addonOptions.map((addon) => (
                      <div
                        key={addon.value}
                        className="flex items-center space-x-2"
                      >
                        <input
                          type="checkbox"
                          id={`addon-${addon.value}`}
                          value={addon.value}
                          {...register("plan.addons")}
                          className="rounded border-gray-300"
                        />
                        <Label htmlFor={`addon-${addon.value}`}>
                          {addon.label}
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="pricing-ref">
                    Pricing Reference (Optional)
                  </Label>
                  <Input
                    id="pricing-ref"
                    {...register("plan.pricing_ref")}
                    placeholder="Enter pricing reference"
                  />
                </div>
              </div>

              {/* Slug Preview */}
              {slugPreview && (
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Globe className="h-4 w-4" />
                    <span>Public URL preview:</span>
                  </div>
                  <code className="block mt-1 text-sm font-mono text-blue-600">
                    {env.PUBLIC_HOST_DOMAIN}
                    {slugPreview}
                  </code>
                </div>
              )}
            </div>

            {/* Fixed button section at bottom */}
            <div className="p-6 border-t bg-white flex-shrink-0 pointer-events-auto">
              <div className="flex space-x-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleClose}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={false}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50"
                >
                  Create Tenant
                </Button>
              </div>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
