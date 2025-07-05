'use client'

import { motion } from 'framer-motion'
import { Bell, Search, User, Activity } from 'lucide-react'

export default function Header() {
  return (
    <motion.header
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="bg-background-secondary/50 backdrop-blur-sm border-b border-purple-primary/20 px-6 py-4"
    >
      <div className="flex items-center justify-between">
        {/* Search Bar */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-medium w-4 h-4" />
            <input
              type="text"
              placeholder="Search research, experiments, or data..."
              className="w-full pl-10 pr-4 py-2 bg-background-tertiary border border-purple-primary/30 rounded-lg text-gray-light placeholder-gray-medium focus:outline-none focus:border-purple-primary focus:ring-2 focus:ring-purple-primary/20 transition-all duration-200"
            />
          </div>
        </div>

        {/* Status and Actions */}
        <div className="flex items-center space-x-4">
          {/* System Status */}
          <div className="flex items-center space-x-2 px-3 py-1 bg-background-tertiary rounded-full">
            <Activity className="w-4 h-4 text-green-500" />
            <span className="text-sm text-gray-light">Active</span>
          </div>

          {/* Notifications */}
          <button className="relative p-2 rounded-lg hover:bg-background-tertiary transition-colors">
            <Bell className="w-5 h-5 text-gray-medium" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-purple-primary rounded-full"></span>
          </button>

          {/* User Profile */}
          <button className="flex items-center space-x-2 p-2 rounded-lg hover:bg-background-tertiary transition-colors">
            <div className="w-8 h-8 bg-gradient-to-r from-purple-primary to-purple-accent rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
            <span className="text-sm text-gray-light">Researcher</span>
          </button>
        </div>
      </div>
    </motion.header>
  )
}
