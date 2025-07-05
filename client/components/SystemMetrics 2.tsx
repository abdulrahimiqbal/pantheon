'use client'

import { motion } from 'framer-motion'
import { Cpu, HardDrive, Zap, Wifi } from 'lucide-react'

export default function SystemMetrics() {
  const metrics = [
    {
      label: 'CPU Usage',
      value: 68,
      icon: Cpu,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/20'
    },
    {
      label: 'Memory',
      value: 45,
      icon: HardDrive,
      color: 'text-green-400',
      bgColor: 'bg-green-500/20'
    },
    {
      label: 'Power',
      value: 92,
      icon: Zap,
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-500/20'
    },
    {
      label: 'Network',
      value: 78,
      icon: Wifi,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/20'
    }
  ]

  return (
    <div className="space-y-4">
      {metrics.map((metric, index) => {
        const Icon = metric.icon
        
        return (
          <motion.div
            key={metric.label}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className="space-y-2"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Icon className={`w-4 h-4 ${metric.color}`} />
                <span className="text-sm text-gray-light">{metric.label}</span>
              </div>
              <span className="text-sm font-medium text-white">{metric.value}%</span>
            </div>
            
            <div className="w-full bg-background-tertiary rounded-full h-2">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${metric.value}%` }}
                transition={{ duration: 1, delay: index * 0.2 }}
                className={`h-2 rounded-full ${metric.bgColor} relative overflow-hidden`}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"></div>
              </motion.div>
            </div>
          </motion.div>
        )
      })}
      
      <div className="pt-4 border-t border-purple-primary/20">
        <div className="text-center">
          <p className="text-xs text-gray-medium">Last updated: 2 seconds ago</p>
        </div>
      </div>
    </div>
  )
}
