import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'CareerOS AI - Intelligent Job Search',
  description: 'AI-powered job search and application tracking platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
