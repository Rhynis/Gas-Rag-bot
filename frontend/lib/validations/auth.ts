import { z } from 'zod'

const phoneRegex = /^(\+84|0)[1-9][0-9]{8,9}$/

export const passwordSchema = z
  .string()
  .min(12, 'Mật khẩu phải có ít nhất 12 ký tự')
  .regex(/[A-Z]/, 'Mật khẩu phải có chữ hoa')
  .regex(/[a-z]/, 'Mật khẩu phải có chữ thường')
  .regex(/[0-9]/, 'Mật khẩu phải có chữ số')
  .regex(/[^A-Za-z0-9]/, 'Mật khẩu phải có ký tự đặc biệt')

export const loginSchema = z.object({
  email: z.string().min(1, 'Email không được để trống').email('Email không hợp lệ'),
  password: z.string().min(1, 'Mật khẩu không được để trống'),
})

export const registerSchema = z
  .object({
    full_name: z.string().min(2, 'Họ tên phải có ít nhất 2 ký tự').max(255, 'Họ tên quá dài'),
    email: z.string().email('Email không hợp lệ'),
    phone: z.string().regex(phoneRegex, 'Số điện thoại không hợp lệ (VD: 0901234567)'),
    password: passwordSchema,
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Mật khẩu xác nhận không khớp',
    path: ['confirmPassword'],
  })

export const passwordChangeSchema = z
  .object({
    oldPassword: z.string().min(1, 'Vui lòng nhập mật khẩu cũ'),
    newPassword: passwordSchema,
    confirmNewPassword: z.string(),
  })
  .refine((data) => data.newPassword === data.confirmNewPassword, {
    message: 'Mật khẩu xác nhận không khớp',
    path: ['confirmNewPassword'],
  })

export const passwordResetRequestSchema = z.object({
  email: z.string().email('Email không hợp lệ'),
})

export const passwordResetSchema = z
  .object({
    token: z.string().optional(),
    newPassword: passwordSchema,
    confirmNewPassword: z.string(),
  })
  .refine((data) => data.newPassword === data.confirmNewPassword, {
    message: 'Mật khẩu xác nhận không khớp',
    path: ['confirmNewPassword'],
  })

export type LoginFormValues = z.infer<typeof loginSchema>
export type RegisterFormValues = z.infer<typeof registerSchema>
export type PasswordChangeFormValues = z.infer<typeof passwordChangeSchema>
export type PasswordResetRequestValues = z.infer<typeof passwordResetRequestSchema>
export type PasswordResetValues = z.infer<typeof passwordResetSchema>
