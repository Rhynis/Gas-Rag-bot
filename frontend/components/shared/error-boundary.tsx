'use client'

import { Component, type ErrorInfo, type ReactNode } from 'react'

type Props = {
  children: ReactNode
  fallback?: ReactNode
}

type State = {
  hasError: boolean
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(): State {
    return { hasError: true }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error boundary caught error', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? <p>Đã có lỗi xảy ra. Vui lòng thử lại.</p>
    }
    return this.props.children
  }
}
