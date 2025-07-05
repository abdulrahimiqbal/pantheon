'use client'

import { motion } from 'framer-motion'
import { LucideIcon } from 'lucide-react'

interface MetricCardProps {
  title: string
  value: string
  change: string
  icon: LucideIcon
  color: string
}

export default function MetricCard({ title, value, change, icon: Icon, color }: MetricCardProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className="glass-panel p-6 cursor-pointer"
    >
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg bg-background-tertiary ${color}`}>
          <Icon className="w-6 h-6" />
        </div>
        <span className="text-sm text-green-400 font-medium">
          {change}
        </span>
      </div>
      
      <div>
        <h3 className="text-2xl font-bold text-white mb-1">
          {value}
        </h3>
        <p className="text-gray-medium text-sm">
          {title}
        </p>
      </div>
    </motion.div>
  )
}
