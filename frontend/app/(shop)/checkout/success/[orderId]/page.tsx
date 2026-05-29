import { SuccessClient } from './success-client'

type SuccessPageProps = {
  params: Promise<{ orderId: string }>
}

export default async function CheckoutSuccessPage({ params }: SuccessPageProps) {
  const { orderId } = await params
  return <SuccessClient orderId={orderId} />
}
