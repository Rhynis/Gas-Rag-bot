'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import * as adminApi from '@/lib/api/admin'
import type { UserRole } from '@/lib/api/auth'
import type { AdminUserSearchParams } from '@/lib/api/admin'

export const adminKeys = {
  all: ['admin'] as const,
  dashboard: () => [...adminKeys.all, 'dashboard'] as const,
  users: () => [...adminKeys.all, 'users'] as const,
  userList: (params: AdminUserSearchParams) => [...adminKeys.users(), params] as const,
}

export function useAdminDashboard() {
  return useQuery({
    queryKey: adminKeys.dashboard(),
    queryFn: adminApi.getAdminDashboard,
  })
}

export function useAdminUsers(params: AdminUserSearchParams = {}) {
  return useQuery({
    queryKey: adminKeys.userList(params),
    queryFn: () => adminApi.getAdminUsers(params),
  })
}

export function useUpdateAdminUserRole() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ userId, role }: { userId: string; role: UserRole }) =>
      adminApi.updateAdminUserRole(userId, role),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: adminKeys.users() })
      await queryClient.invalidateQueries({ queryKey: adminKeys.dashboard() })
      toast.success('Đã cập nhật vai trò')
    },
  })
}

export function useUpdateAdminUserStatus() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ userId, isActive }: { userId: string; isActive: boolean }) =>
      adminApi.updateAdminUserStatus(userId, isActive),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: adminKeys.users() })
      await queryClient.invalidateQueries({ queryKey: adminKeys.dashboard() })
      toast.success('Đã cập nhật trạng thái')
    },
  })
}
