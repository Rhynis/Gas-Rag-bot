import axios, { type AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'
import { v4 as uuidv4 } from 'uuid'
import { createClient } from '@/lib/supabase/client'

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    public detail: string
  ) {
    super(detail)
    this.name = 'ApiError'
  }
}

/** Create an Axios instance configured for the GasBot API. */
function createApiClient(): AxiosInstance {
  const client = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000',
    timeout: 30000,
    headers: { 'Content-Type': 'application/json' },
  })

  client.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
    const supabase = createClient()
    const {
      data: { session },
    } = await supabase.auth.getSession()

    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`
    }

    const method = config.method?.toUpperCase()
    if (method === 'POST' || method === 'PATCH' || method === 'PUT') {
      if (!config.headers['Idempotency-Key']) {
        config.headers['Idempotency-Key'] = uuidv4()
      }
    }

    return config
  })

  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      if (error.response) {
        const data = error.response.data as { detail?: string; error_code?: string }
        throw new ApiError(
          error.response.status,
          data.error_code ?? 'unknown_error',
          data.detail ?? error.message
        )
      }
      if (error.request) {
        throw new ApiError(0, 'network_error', 'Network error - please check your connection')
      }
      throw new ApiError(0, 'unknown_error', error.message)
    }
  )

  return client
}

export const apiClient = createApiClient()
