import { type NextRequest, NextResponse } from 'next/server'
import { updateSession } from '@/lib/supabase/middleware'

/** Next.js middleware for authentication and route protection. */
export async function middleware(request: NextRequest) {
  const { response, user } = await updateSession(request)
  const pathname = request.nextUrl.pathname

  const publicRoutes = ['/', '/products', '/track', '/login', '/register']
  const isPublic = publicRoutes.some(
    (route) => pathname === route || pathname.startsWith(route + '/')
  )

  if (pathname.startsWith('/admin')) {
    if (!user) {
      const url = request.nextUrl.clone()
      url.pathname = '/login'
      url.searchParams.set('redirectTo', pathname)
      return NextResponse.redirect(url)
    }
    const role = user.user_metadata?.role
    if (role !== 'admin') {
      const url = request.nextUrl.clone()
      url.pathname = '/'
      return NextResponse.redirect(url)
    }
  }

  if (!isPublic && !user) {
    const url = request.nextUrl.clone()
    url.pathname = '/login'
    url.searchParams.set('redirectTo', pathname)
    return NextResponse.redirect(url)
  }

  return response
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)'],
}
