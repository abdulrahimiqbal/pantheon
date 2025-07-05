import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Pantheon - AI Physics Research Platform',
  description: 'Autonomous AI-driven physics research and hypothesis generation platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-background-primary via-background-secondary to-background-tertiary">
          {children}
        </div>
      </body>
    </html>
  )
}
