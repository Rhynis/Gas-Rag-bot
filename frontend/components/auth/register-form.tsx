'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import Link from 'next/link'
import { useMemo } from 'react'
import { useForm, useWatch } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/lib/hooks/use-auth'
import { registerSchema, type RegisterFormValues } from '@/lib/validations/auth'

function getPasswordScore(password: string): number {
  return [
    password.length >= 12,
    /[A-Z]/.test(password),
    /[a-z]/.test(password),
    /[0-9]/.test(password),
    /[^A-Za-z0-9]/.test(password),
  ].filter(Boolean).length
}

export function RegisterForm() {
  const { register: registerUser, isLoading } = useAuth()
  const {
    register,
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      full_name: '',
      email: '',
      phone: '',
      password: '',
      confirmPassword: '',
    },
  })
  const password = useWatch({ control, name: 'password' })
  const strength = useMemo(() => getPasswordScore(password), [password])

  return (
    <form className="space-y-5" onSubmit={handleSubmit(registerUser)}>
      <div className="space-y-2">
        <label className="text-sm font-medium" htmlFor="full_name">
          Họ và tên
        </label>
        <input
          id="full_name"
          autoComplete="name"
          className="h-10 w-full rounded-md border px-3 text-sm outline-none focus:ring-2 focus:ring-ring"
          {...register('full_name')}
        />
        {errors.full_name ? (
          <p className="text-sm text-red-600">{errors.full_name.message}</p>
        ) : null}
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium" htmlFor="email">
          Email
        </label>
        <input
          id="email"
          autoComplete="email"
          className="h-10 w-full rounded-md border px-3 text-sm outline-none focus:ring-2 focus:ring-ring"
          {...register('email')}
        />
        {errors.email ? <p className="text-sm text-red-600">{errors.email.message}</p> : null}
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium" htmlFor="phone">
          Số điện thoại
        </label>
        <input
          id="phone"
          autoComplete="tel"
          className="h-10 w-full rounded-md border px-3 text-sm outline-none focus:ring-2 focus:ring-ring"
          {...register('phone')}
        />
        {errors.phone ? <p className="text-sm text-red-600">{errors.phone.message}</p> : null}
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium" htmlFor="password">
          Mật khẩu
        </label>
        <input
          id="password"
          type="password"
          autoComplete="new-password"
          className="h-10 w-full rounded-md border px-3 text-sm outline-none focus:ring-2 focus:ring-ring"
          {...register('password')}
        />
        <div className="grid grid-cols-5 gap-1" aria-hidden="true">
          {Array.from({ length: 5 }).map((_, index) => (
            <span
              className={
                index < strength
                  ? 'h-1 rounded bg-primary text-primary-foreground'
                  : 'h-1 rounded bg-slate-200'
              }
              key={index}
            />
          ))}
        </div>
        {errors.password ? <p className="text-sm text-red-600">{errors.password.message}</p> : null}
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium" htmlFor="confirmPassword">
          Xác nhận mật khẩu
        </label>
        <input
          id="confirmPassword"
          type="password"
          autoComplete="new-password"
          className="h-10 w-full rounded-md border px-3 text-sm outline-none focus:ring-2 focus:ring-ring"
          {...register('confirmPassword')}
        />
        {errors.confirmPassword ? (
          <p className="text-sm text-red-600">{errors.confirmPassword.message}</p>
        ) : null}
      </div>

      <Button className="w-full" disabled={isLoading || isSubmitting} type="submit">
        {isLoading || isSubmitting ? 'Đang tạo tài khoản...' : 'Đăng ký'}
      </Button>

      <p className="text-center text-sm text-slate-600">
        Đã có tài khoản?{' '}
        <Link className="text-primary hover:underline" href="/login">
          Đăng nhập
        </Link>
      </p>
    </form>
  )
}
