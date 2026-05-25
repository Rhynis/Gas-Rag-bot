import { describe, expect, it } from 'vitest'
import { loginSchema, registerSchema } from '@/lib/validations/auth'

describe('auth validation schemas', () => {
  it('accepts valid registration data', () => {
    const result = registerSchema.safeParse({
      full_name: 'Nguyen Van A',
      email: 'user@example.com',
      phone: '0901234567',
      password: 'StrongPass123!',
      confirmPassword: 'StrongPass123!',
    })

    expect(result.success).toBe(true)
  })

  it('rejects weak passwords with Vietnamese messages', () => {
    const result = registerSchema.safeParse({
      full_name: 'Nguyen Van A',
      email: 'user@example.com',
      phone: '0901234567',
      password: 'weak',
      confirmPassword: 'weak',
    })

    expect(result.success).toBe(false)
    expect(result.success ? '' : result.error.issues[0]?.message).toContain('Mật khẩu')
  })

  it('rejects mismatched confirmation password', () => {
    const result = registerSchema.safeParse({
      full_name: 'Nguyen Van A',
      email: 'user@example.com',
      phone: '0901234567',
      password: 'StrongPass123!',
      confirmPassword: 'OtherPass123!',
    })

    expect(result.success).toBe(false)
    expect(result.success ? '' : result.error.issues.at(-1)?.message).toBe(
      'Mật khẩu xác nhận không khớp'
    )
  })

  it('requires login email and password', () => {
    const result = loginSchema.safeParse({ email: '', password: '' })

    expect(result.success).toBe(false)
  })
})
