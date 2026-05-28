'use client'

import type { FormEvent, ReactNode } from 'react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Textarea } from '@/components/ui/textarea'
import { productSchema } from '@/lib/validations/product'
import type { Product, ProductCreateInput, ProductUpdateInput } from '@/types/product'

type ProductFormState = {
  sku: string
  name: string
  brand: string
  size_kg: string
  price: string
  stock_quantity: string
  description: string
  image_url: string
  safety_info: string
  is_active: boolean
}

type ProductFormProps = {
  product?: Product
  isSubmitting?: boolean
  onSubmit: (data: ProductCreateInput | ProductUpdateInput) => Promise<void>
}

const emptyState: ProductFormState = {
  sku: '',
  name: '',
  brand: '',
  size_kg: '12',
  price: '',
  stock_quantity: '0',
  description: '',
  image_url: '',
  safety_info: '',
  is_active: true,
}

function initialState(product?: Product): ProductFormState {
  if (!product) return emptyState
  return {
    sku: product.sku,
    name: product.name,
    brand: product.brand,
    size_kg: Number(product.size_kg).toString(),
    price: Number(product.price).toString(),
    stock_quantity: product.stock_quantity.toString(),
    description: product.description ?? '',
    image_url: product.image_url ?? '',
    safety_info: product.safety_info ?? '',
    is_active: product.is_active,
  }
}

function normalizeText(value: string): string | null {
  const trimmed = value.trim()
  return trimmed ? trimmed : null
}

export function ProductForm({ product, isSubmitting = false, onSubmit }: ProductFormProps) {
  const [form, setForm] = useState<ProductFormState>(() => initialState(product))
  const [errors, setErrors] = useState<Record<string, string>>({})

  function updateField(field: keyof ProductFormState, value: string | boolean) {
    setForm((current) => ({ ...current, [field]: value }))
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const parsed = productSchema.safeParse({
      ...form,
      stock_quantity: Number.parseInt(form.stock_quantity, 10),
    })

    if (!parsed.success) {
      const fieldErrors: Record<string, string> = {}
      Object.entries(parsed.error.flatten().fieldErrors).forEach(([field, messages]) => {
        if (messages?.[0]) fieldErrors[field] = messages[0]
      })
      setErrors(fieldErrors)
      return
    }

    setErrors({})
    await onSubmit({
      ...parsed.data,
      description: normalizeText(form.description),
      image_url: normalizeText(form.image_url),
      safety_info: normalizeText(form.safety_info),
      ...(product ? { is_active: form.is_active } : {}),
    })
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <div className="grid gap-4 md:grid-cols-2">
        <FieldError label="SKU" error={errors.sku}>
          <Input value={form.sku} onChange={(event) => updateField('sku', event.target.value)} />
        </FieldError>
        <FieldError label="Tên sản phẩm" error={errors.name}>
          <Input value={form.name} onChange={(event) => updateField('name', event.target.value)} />
        </FieldError>
        <FieldError label="Thương hiệu" error={errors.brand}>
          <Input
            value={form.brand}
            onChange={(event) => updateField('brand', event.target.value)}
          />
        </FieldError>
        <FieldError label="Kích thước" error={errors.size_kg}>
          <Select value={form.size_kg} onValueChange={(value) => updateField('size_kg', value)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="6">6kg</SelectItem>
              <SelectItem value="12">12kg</SelectItem>
              <SelectItem value="45">45kg</SelectItem>
            </SelectContent>
          </Select>
        </FieldError>
        <FieldError label="Giá" error={errors.price}>
          <Input
            inputMode="numeric"
            value={form.price}
            onChange={(event) => updateField('price', event.target.value)}
          />
        </FieldError>
        <FieldError label="Tồn kho" error={errors.stock_quantity}>
          <Input
            inputMode="numeric"
            value={form.stock_quantity}
            onChange={(event) => updateField('stock_quantity', event.target.value)}
          />
        </FieldError>
      </div>

      <FieldError label="Hình ảnh" error={errors.image_url}>
        <Input
          placeholder="https://..."
          value={form.image_url}
          onChange={(event) => updateField('image_url', event.target.value)}
        />
      </FieldError>
      <FieldError label="Mô tả" error={errors.description}>
        <Textarea
          value={form.description}
          onChange={(event) => updateField('description', event.target.value)}
        />
      </FieldError>
      <FieldError label="An toàn sử dụng" error={errors.safety_info}>
        <Textarea
          value={form.safety_info}
          onChange={(event) => updateField('safety_info', event.target.value)}
        />
      </FieldError>

      {product ? (
        <label className="flex items-center justify-between rounded-lg border p-3 text-sm">
          Đang bán
          <Switch
            checked={form.is_active}
            onCheckedChange={(value) => updateField('is_active', value)}
          />
        </label>
      ) : null}

      <Button type="submit" disabled={isSubmitting}>
        {product ? 'Lưu thay đổi' : 'Tạo sản phẩm'}
      </Button>
    </form>
  )
}

function FieldError({
  label,
  error,
  children,
}: {
  label: string
  error?: string
  children: ReactNode
}) {
  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      {children}
      {error ? <p className="text-destructive text-sm">{error}</p> : null}
    </div>
  )
}
