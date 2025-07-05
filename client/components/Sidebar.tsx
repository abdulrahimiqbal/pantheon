'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  MessageCircle, 
  BarChart3, 
  Settings, 
  ChevronLeft,
  ChevronRight,
  Atom,
  Plus,
  Trash2,
  Edit3
} from 'lucide-react'

interface Chat {
  id: string
  name: string
  lastMessage: string
  timestamp: string
}

interface SidebarProps {
  activeTab: string
  setActiveTab: (tab: string) => void
  collapsed: boolean
  setCollapsed: (collapsed: boolean) => void
  chats: Chat[]
  activeChat: string | null
  onChatSelect: (chatId: string) => void
  onNewChat: () => void
  onDeleteChat: (chatId: string) => void
  onRenameChat: (chatId: string, newName: string) => void
}

const menuItems = [
  { id: 'chat', label: 'Chat', icon: MessageCircle },
  { id: 'visualization', label: 'Visualization', icon: BarChart3 },
  { id: 'config', label: 'Configuration', icon: Settings },
]

export default function Sidebar({ 
  activeTab, 
  setActiveTab, 
  collapsed, 
  setCollapsed,
  chats,
  activeChat,
  onChatSelect,
  onNewChat,
  onDeleteChat,
  onRenameChat
}: SidebarProps) {
  const [editingChat, setEditingChat] = useState<string | null>(null)
  const [editName, setEditName] = useState('')
  return (
    <motion.div
      initial={{ x: -300 }}
      animate={{ x: 0, width: collapsed ? 80 : 280 }}
      transition={{ duration: 0.3 }}
      className="bg-background-secondary border-r border-orange-primary/20 flex flex-col"
    >
      {/* Header */}
      <div className="p-6 border-b border-orange-primary/20">
        <div className="flex items-center justify-between">
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="flex items-center space-x-3"
            >
              <div className="w-8 h-8 bg-gradient-to-r from-orange-primary to-orange-accent rounded-lg flex items-center justify-center">
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
                      ? 'bg-gradient-to-r from-orange-primary to-orange-secondary text-white shadow-lg'
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

      {/* Chat History Section */}
      {activeTab === 'chat' && (
        <div className="flex-1 px-4 pb-4">
          <div className="flex items-center justify-between mb-3">
            {!collapsed && (
              <h3 className="text-sm font-medium text-gray-medium">Chat History</h3>
            )}
            <button
              onClick={onNewChat}
              className="p-1.5 rounded-lg hover:bg-background-tertiary transition-colors"
              title="New Chat"
            >
              <Plus className="w-4 h-4 text-gray-medium hover:text-white" />
            </button>
          </div>
          
          <div className="space-y-1 max-h-64 overflow-y-auto">
            {chats.map((chat) => (
              <div
                key={chat.id}
                className={`group flex items-center space-x-2 p-2 rounded-lg cursor-pointer transition-all duration-200 ${
                  activeChat === chat.id
                    ? 'bg-orange-primary/20 border border-orange-primary/30'
                    : 'hover:bg-background-tertiary'
                }`}
                onClick={() => onChatSelect(chat.id)}
              >
                <MessageCircle className="w-4 h-4 text-gray-medium flex-shrink-0" />
                
                {!collapsed && (
                  <>
                    {editingChat === chat.id ? (
                      <input
                        type="text"
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        onBlur={() => {
                          if (editName.trim()) {
                            onRenameChat(chat.id, editName.trim())
                          }
                          setEditingChat(null)
                        }}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            if (editName.trim()) {
                              onRenameChat(chat.id, editName.trim())
                            }
                            setEditingChat(null)
                          } else if (e.key === 'Escape') {
                            setEditingChat(null)
                          }
                        }}
                        className="flex-1 bg-background-secondary border border-orange-primary/30 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-orange-primary"
                        autoFocus
                      />
                    ) : (
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-white truncate">{chat.name}</p>
                        <p className="text-xs text-gray-medium truncate">{chat.lastMessage}</p>
                      </div>
                    )}
                    
                    <div className="opacity-0 group-hover:opacity-100 flex space-x-1 transition-opacity">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setEditingChat(chat.id)
                          setEditName(chat.name)
                        }}
                        className="p-1 rounded hover:bg-background-secondary transition-colors"
                        title="Rename"
                      >
                        <Edit3 className="w-3 h-3 text-gray-medium hover:text-white" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          onDeleteChat(chat.id)
                        }}
                        className="p-1 rounded hover:bg-red-500/20 transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-3 h-3 text-gray-medium hover:text-red-400" />
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))}
            
            {chats.length === 0 && !collapsed && (
              <div className="text-center py-4">
                <p className="text-xs text-gray-medium">No chats yet</p>
                <p className="text-xs text-gray-medium">Click + to start</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Status Indicator */}
      <div className="p-4 border-t border-orange-primary/20">
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
