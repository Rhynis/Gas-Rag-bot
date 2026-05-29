'use client'

import { useMemo, useState } from 'react'
import { toast } from 'sonner'
import { UserTable } from '@/components/admin/user/user-table'
import { EmptyState } from '@/components/shared/empty-state'
import { PageHeader } from '@/components/shared/page-header'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import type { AdminUser, AdminUserSearchParams } from '@/lib/api/admin'
import type { UserRole } from '@/lib/api/auth'
import {
  useAdminUsers,
  useUpdateAdminUserRole,
  useUpdateAdminUserStatus,
} from '@/lib/hooks/use-admin'
import { useAuth } from '@/lib/hooks/use-auth'

export default function AdminUsersPage() {
  const { user } = useAuth()
  const [email, setEmail] = useState('')
  const [role, setRole] = useState<UserRole | ''>('')
  const [status, setStatus] = useState<'all' | 'active' | 'inactive'>('all')
  const [params, setParams] = useState<AdminUserSearchParams>({ limit: 50 })
  const usersQuery = useAdminUsers(params)
  const roleMutation = useUpdateAdminUserRole()
  const statusMutation = useUpdateAdminUserStatus()

  const totalText = useMemo(() => {
    const total = usersQuery.data?.total ?? 0
    return `${total.toLocaleString('vi-VN')} người dùng`
  }, [usersQuery.data?.total])

  function applyFilters() {
    setParams({
      limit: 50,
      email: email.trim() || undefined,
      role: role || undefined,
      is_active: status === 'all' ? undefined : status === 'active',
    })
  }

  async function handleRoleChange(target: AdminUser, nextRole: UserRole) {
    try {
      await roleMutation.mutateAsync({ userId: target.id, role: nextRole })
    } catch (caught) {
      toast.error(caught instanceof Error ? caught.message : 'Không thể cập nhật vai trò')
    }
  }

  async function handleStatusChange(target: AdminUser, isActive: boolean) {
    try {
      await statusMutation.mutateAsync({ userId: target.id, isActive })
    } catch (caught) {
      toast.error(caught instanceof Error ? caught.message : 'Không thể cập nhật trạng thái')
    }
  }

  const users = usersQuery.data?.items ?? []

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <PageHeader
          title="Quản lý người dùng"
          description="Tìm kiếm, phân quyền và khóa tài khoản khi cần."
        />
        <div className="rounded-md border bg-white px-3 py-2 text-sm font-medium text-slate-700">
          {totalText}
        </div>
      </div>

      <div className="flex flex-wrap gap-3 rounded-lg border bg-white p-4">
        <Input
          className="w-full sm:w-72"
          placeholder="Email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />
        <select
          className="h-10 rounded-md border bg-white px-3 text-sm"
          value={role}
          onChange={(event) => setRole(event.target.value as UserRole | '')}
        >
          <option value="">Tất cả vai trò</option>
          <option value="customer">Khách hàng</option>
          <option value="staff">Nhân viên</option>
          <option value="admin">Quản trị</option>
        </select>
        <select
          className="h-10 rounded-md border bg-white px-3 text-sm"
          value={status}
          onChange={(event) => setStatus(event.target.value as 'all' | 'active' | 'inactive')}
        >
          <option value="all">Tất cả trạng thái</option>
          <option value="active">Đang hoạt động</option>
          <option value="inactive">Đã khóa</option>
        </select>
        <Button onClick={applyFilters}>Lọc</Button>
      </div>

      <div className="overflow-x-auto rounded-lg border bg-white">
        <UserTable
          users={users}
          currentUserId={user?.id}
          isLoading={usersQuery.isLoading}
          isUpdating={roleMutation.isPending || statusMutation.isPending}
          onRoleChange={(target, nextRole) => void handleRoleChange(target, nextRole)}
          onStatusChange={(target, isActive) => void handleStatusChange(target, isActive)}
        />
        {!usersQuery.isLoading && users.length === 0 ? (
          <div className="p-6">
            <EmptyState title="Không có người dùng" description="Thử đổi bộ lọc hiện tại." />
          </div>
        ) : null}
      </div>
    </section>
  )
}
