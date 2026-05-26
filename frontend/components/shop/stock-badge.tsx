import { Badge } from '@/components/ui/badge'

type StockBadgeProps = {
  stockQuantity: number
}

export function StockBadge({ stockQuantity }: StockBadgeProps) {
  if (stockQuantity === 0) {
    return <Badge className="bg-safety text-safety-foreground hover:bg-safety/90">Hết hàng</Badge>
  }

  if (stockQuantity <= 10) {
    return <Badge className="bg-yellow-100 text-yellow-900 hover:bg-yellow-100">Sắp hết hàng</Badge>
  }

  return <Badge>Còn hàng</Badge>
}
