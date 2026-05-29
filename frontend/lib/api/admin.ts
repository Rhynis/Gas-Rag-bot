import { apiClient } from '@/lib/api/client'
import type { UserRole } from '@/lib/api/auth'

export interface AdminDashboardStats {
  orders_today: number
  orders_pending: number
  revenue_today: number
  low_stock_count: number
  users_total: number
  users_new_today: number
}

export interface AdminUser {
  id: string
  email: string
  full_name: string | null
  phone: string | null
  role: UserRole
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface AdminUserListResponse {
  items: AdminUser[]
  total: number
  page: number
  limit: number
  has_more: boolean
}

export interface AdminUserSearchParams {
  email?: string
  role?: UserRole
  is_active?: boolean
  skip?: number
  limit?: number
}

export async function getAdminDashboard(): Promise<AdminDashboardStats> {
  const response = await apiClient.get<AdminDashboardStats>('/api/v1/admin/dashboard')
  return response.data
}

export async function getAdminUsers(
  params: AdminUserSearchParams = {}
): Promise<AdminUserListResponse> {
  const response = await apiClient.get<AdminUserListResponse>('/api/v1/admin/users', { params })
  return response.data
}

export async function updateAdminUserRole(userId: string, role: UserRole): Promise<AdminUser> {
  const response = await apiClient.patch<AdminUser>(`/api/v1/admin/users/${userId}/role`, {
    role,
  })
  return response.data
}

export async function updateAdminUserStatus(userId: string, isActive: boolean): Promise<AdminUser> {
  const response = await apiClient.patch<AdminUser>(`/api/v1/admin/users/${userId}/status`, {
    is_active: isActive,
  })
  return response.data
}
