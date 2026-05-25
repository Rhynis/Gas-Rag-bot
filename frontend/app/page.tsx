import Link from 'next/link'
import { Bot, ShieldCheck, Truck } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const features = [
  {
    title: 'AI hỗ trợ 24/7',
    description: 'Tư vấn sản phẩm, đặt hàng và giải đáp an toàn sử dụng gas.',
    icon: Bot,
  },
  {
    title: 'Giao hàng nhanh',
    description: 'Giao tận nơi trong khu vực hỗ trợ với quy trình rõ ràng.',
    icon: Truck,
  },
  {
    title: 'An toàn ưu tiên',
    description: 'Nội dung an toàn được kiểm soát, ưu tiên tình huống khẩn cấp.',
    icon: ShieldCheck,
  },
]

export default function HomePage() {
  return (
    <div>
      <section className="bg-white">
        <div className="mx-auto grid max-w-6xl gap-10 px-4 py-16 md:grid-cols-[1.1fr_0.9fr] md:items-center">
          <div className="space-y-6">
            <h1 className="max-w-3xl text-4xl font-semibold tracking-normal text-slate-950 md:text-6xl">
              Mua gas LPG dễ dàng với AI hỗ trợ
            </h1>
            <p className="max-w-xl text-lg text-slate-600">
              Giao hàng tận nơi, an toàn, nhanh chóng.
            </p>
            <Button asChild size="lg">
              <Link href="/products">Xem sản phẩm</Link>
            </Button>
          </div>
          <div className="rounded-lg border bg-orange-50 p-8">
            <div className="aspect-[4/3] rounded-md bg-gradient-to-br from-orange-200 via-white to-red-100" />
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-12">
        <div className="grid gap-4 md:grid-cols-3">
          {features.map((feature) => (
            <Card key={feature.title}>
              <CardHeader>
                <feature.icon className="h-6 w-6 text-orange-700" />
                <CardTitle className="text-xl">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    </div>
  )
}
