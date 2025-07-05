'use client'

import { motion } from 'framer-motion'
import { LucideIcon } from 'lucide-react'

interface Activity {
  id: number
  type: string
  title: string
  status: string
  timestamp: string
  icon: LucideIcon
  color: string
}

interface ActivityTimelineProps {
  activities: Activity[]
}

export default function ActivityTimeline({ activities }: ActivityTimelineProps) {
  return (
    <div className="space-y-4">
      {activities.map((activity, index) => {
        const Icon = activity.icon
        
        return (
          <motion.div
            key={activity.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className="flex items-start space-x-4 p-4 rounded-lg bg-background-tertiary/50 hover:bg-background-tertiary transition-colors"
          >
            <div className={`p-2 rounded-lg bg-background-secondary ${activity.color}`}>
              <Icon className="w-4 h-4" />
            </div>
            
            <div className="flex-1 min-w-0">
              <h4 className="text-white font-medium truncate">
                {activity.title}
              </h4>
              <div className="flex items-center space-x-2 mt-1">
                <span className={`text-xs px-2 py-1 rounded-full ${
                  activity.status === 'completed' 
                    ? 'bg-green-500/20 text-green-400'
                    : activity.status === 'in-progress'
                    ? 'bg-yellow-500/20 text-yellow-400'
                    : activity.status === 'attention'
                    ? 'bg-red-500/20 text-red-400'
                    : 'bg-purple-500/20 text-purple-400'
                }`}>
                  {activity.status}
                </span>
                <span className="text-xs text-gray-medium">
                  {activity.timestamp}
                </span>
              </div>
            </div>
          </motion.div>
        )
      })}
      
      <div className="text-center pt-4">
        <button className="text-purple-primary hover:text-purple-secondary text-sm font-medium transition-colors">
          View All Activities
        </button>
      </div>
    </div>
  )
}
