type LowStockAlertProps = {
  count: number
}

export function LowStockAlert({ count }: LowStockAlertProps) {
  if (count === 0) return null

  return (
    <div className="rounded-lg border border-primary/30 bg-primary/10 p-4 text-sm text-slate-800">
      {count.toLocaleString('vi-VN')} sản phẩm đang ở mức tồn kho thấp.
    </div>
  )
}
