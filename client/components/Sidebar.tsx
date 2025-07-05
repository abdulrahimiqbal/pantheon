'use client'

import { motion } from 'framer-motion'
import { 
  LayoutDashboard, 
  FlaskConical, 
  BarChart3, 
  Settings, 
  ChevronLeft,
  ChevronRight,
  Atom
} from 'lucide-react'

interface SidebarProps {
  activeTab: string
  setActiveTab: (tab: string) => void
  collapsed: boolean
  setCollapsed: (collapsed: boolean) => void
}

const menuItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'research', label: 'Research', icon: FlaskConical },
  { id: 'visualization', label: 'Visualization', icon: BarChart3 },
  { id: 'config', label: 'Configuration', icon: Settings },
]

export default function Sidebar({ activeTab, setActiveTab, collapsed, setCollapsed }: SidebarProps) {
  return (
    <motion.div
      initial={{ x: -300 }}
      animate={{ x: 0, width: collapsed ? 80 : 280 }}
      transition={{ duration: 0.3 }}
      className="bg-background-secondary border-r border-purple-primary/20 flex flex-col"
    >
      {/* Header */}
      <div className="p-6 border-b border-purple-primary/20">
        <div className="flex items-center justify-between">
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="flex items-center space-x-3"
            >
              <div className="w-8 h-8 bg-gradient-to-r from-purple-primary to-purple-accent rounded-lg flex items-center justify-center">
                <Atom className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Pantheon</h1>
                <p className="text-xs text-gray-medium">AI Physics Research</p>
              </div>
            </motion.div>
          )}
          
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-2 rounded-lg hover:bg-background-tertiary transition-colors"
          >
            {collapsed ? (
              <ChevronRight className="w-4 h-4 text-gray-medium" />
            ) : (
              <ChevronLeft className="w-4 h-4 text-gray-medium" />
            )}
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = activeTab === item.id
            
            return (
              <li key={item.id}>
                <button
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-purple-primary to-purple-secondary text-white shadow-lg'
                      : 'text-gray-medium hover:text-white hover:bg-background-tertiary'
                  }`}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  {!collapsed && (
                    <motion.span
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.1 }}
                      className="font-medium"
                    >
                      {item.label}
                    </motion.span>
                  )}
                </button>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Status Indicator */}
      <div className="p-4 border-t border-purple-primary/20">
        <div className={`flex items-center ${collapsed ? 'justify-center' : 'space-x-3'}`}>
          <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <p className="text-sm text-gray-medium">System Online</p>
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  )
}
