export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="mx-auto flex min-h-[calc(100vh-73px)] max-w-md items-center px-4 py-12">
      <div className="w-full rounded-lg border bg-white p-6 shadow-sm">{children}</div>
    </div>
  )
}
