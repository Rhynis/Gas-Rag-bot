import { describe, expect, it } from 'vitest'
import { customerDeliverySchema, guestLookupSchema, paymentSchema } from '@/lib/validations/order'

describe('order validation', () => {
  it('requires both different recipient fields', () => {
    const result = customerDeliverySchema.safeParse({
      customer_name: 'Nguyen Van A',
      customer_phone: '0901234567',
      customer_email: '',
      delivery_address: '123 Nguyen Trai',
      delivery_ward: 'Phuong Ben Thanh',
      delivery_district: 'Quan 1',
      delivery_city: 'TP. Hồ Chí Minh',
      delivery_notes: '',
      has_different_recipient: true,
      different_recipient_name: 'Tran Thi B',
      different_recipient_phone: '',
    })

    expect(result.success).toBe(false)
  })

  it('requires VAT fields when invoice is requested', () => {
    const result = paymentSchema.safeParse({
      payment_method: 'cod',
      vat_invoice_requested: true,
      vat_info: { company_name: '', tax_code: '', address: '' },
      customer_notes: '',
    })

    expect(result.success).toBe(false)
  })

  it('accepts guest order lookup data', () => {
    const result = guestLookupSchema.safeParse({
      order_number: 'GB-20260529-0001',
      phone: '0901234567',
    })

    expect(result.success).toBe(true)
  })
})
