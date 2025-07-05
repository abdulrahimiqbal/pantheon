'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Activity, Brain } from 'lucide-react'
import Sidebar from './Sidebar'
import Header from './Header'
import ResearchPanel from './ResearchPanel'
import VisualizationPanel from './VisualizationPanel'
import ConfigPanel from './ConfigPanel'
import SystemMetrics from './SystemMetrics'
import ActivityTimeline from './ActivityTimeline'

interface Chat {
  id: string
  name: string
  lastMessage: string
  timestamp: string
}

interface Message {
  id: string
  text: string
  type: 'user' | 'assistant'
  timestamp: string
}

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('chat')
  const [collapsed, setCollapsed] = useState(false)
  const [chats, setChats] = useState<Chat[]>([])
  const [activeChat, setActiveChat] = useState<string | null>(null)
  const [messages, setMessages] = useState<{ [chatId: string]: Message[] }>({})

  const metrics = [
    {
      title: 'Active Agents',
      value: '12',
      change: '+2',
      icon: Brain,
      color: 'text-orange-primary'
    },
    {
      title: 'Experiments Running',
      value: '8',
      change: '+3',
      icon: Brain,
      color: 'text-blue-400'
    },
    {
      title: 'Data Points',
      value: '2.4M',
      change: '+12%',
      icon: Brain,
      color: 'text-green-400'
    },
    {
      title: 'Hypotheses Generated',
      value: '156',
      change: '+8',
      icon: Brain,
      color: 'text-yellow-400'
    }
  ]

  const recentActivities = [
    {
      id: 1,
      type: 'experiment',
      title: 'Quantum Entanglement Analysis',
      status: 'completed',
      timestamp: '2 minutes ago',
      icon: Activity,
      color: 'text-green-400'
    },
    {
      id: 2,
      type: 'hypothesis',
      title: 'Dark Matter Interaction Model',
      status: 'in-progress',
      timestamp: '5 minutes ago',
      icon: Activity,
      color: 'text-yellow-400'
    },
    {
      id: 3,
      type: 'alert',
      title: 'Anomaly Detected in Dataset #47',
      status: 'attention',
      timestamp: '12 minutes ago',
      icon: Activity,
      color: 'text-red-400'
    },
    {
      id: 4,
      type: 'agent',
      title: 'New Agent Deployed: Particle Physics Specialist',
      status: 'active',
      timestamp: '1 hour ago',
      icon: Brain,
      color: 'text-orange-primary'
    }
  ]

  const generateChatId = () => {
    return `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  const generateMessageId = () => {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  const handleNewChat = () => {
    const newChatId = generateChatId()
    const newChat: Chat = {
      id: newChatId,
      name: `New Research Chat ${chats.length + 1}`,
      lastMessage: 'Start your research conversation...',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
    
    setChats(prev => [newChat, ...prev])
    setActiveChat(newChatId)
    setMessages(prev => ({ ...prev, [newChatId]: [] }))
  }

  const handleChatSelect = (chatId: string) => {
    setActiveChat(chatId)
  }

  const handleDeleteChat = (chatId: string) => {
    setChats(prev => prev.filter(chat => chat.id !== chatId))
    setMessages(prev => {
      const newMessages = { ...prev }
      delete newMessages[chatId]
      return newMessages
    })
    
    if (activeChat === chatId) {
      const remainingChats = chats.filter(chat => chat.id !== chatId)
      setActiveChat(remainingChats.length > 0 ? remainingChats[0].id : null)
    }
  }

  const handleRenameChat = (chatId: string, newName: string) => {
    setChats(prev => prev.map(chat => 
      chat.id === chatId ? { ...chat, name: newName } : chat
    ))
  }

  const handleSendMessage = (chatId: string, messageText: string) => {
    const userMessage: Message = {
      id: generateMessageId(),
      text: messageText,
      type: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
    
    setMessages(prev => ({
      ...prev,
      [chatId]: [...(prev[chatId] || []), userMessage]
    }))
    
    // Update chat's last message
    setChats(prev => prev.map(chat => 
      chat.id === chatId 
        ? { ...chat, lastMessage: messageText.substring(0, 50) + (messageText.length > 50 ? '...' : ''), timestamp: userMessage.timestamp }
        : chat
    ))
    
    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: generateMessageId(),
        text: `I understand you're asking about "${messageText.substring(0, 30)}${messageText.length > 30 ? '...' : ''}". This is a fascinating area of physics research. Let me help you explore this topic further with detailed analysis and insights.`,
        type: 'assistant',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
      
      setMessages(prev => ({
        ...prev,
        [chatId]: [...(prev[chatId] || []), aiMessage]
      }))
    }, 2000)
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'chat':
        return (
          <ResearchPanel 
            activeChat={activeChat}
            messages={messages}
            onSendMessage={handleSendMessage}
          />
        )
      case 'visualization':
        return <VisualizationPanel />
      case 'config':
        return <ConfigPanel />
      default:
        return (
          <ResearchPanel 
            activeChat={activeChat}
            messages={messages}
            onSendMessage={handleSendMessage}
          />
        )
    }
  }

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="glass-panel p-6"
      >
        <h1 className="text-3xl font-bold text-white mb-2">
          Welcome to Pantheon
        </h1>
        <p className="text-gray-medium">
          Your AI-driven physics research platform is running smoothly. 
          Monitor your experiments, analyze data, and discover new insights.
        </p>
      </motion.div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <motion.div
            key={metric.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <div className="glass-panel p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-sm text-gray-medium">{metric.title}</p>
                  <p className="text-2xl font-bold text-white">{metric.value}</p>
                </div>
                <div className={`p-3 rounded-lg bg-background-tertiary ${metric.color}`}>
                  <metric.icon className="w-6 h-6" />
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-green-400">{metric.change}</span>
                <span className="text-xs text-gray-medium">vs last hour</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Activity Timeline */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="lg:col-span-2"
        >
          <div className="glass-panel p-6 h-full">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">Recent Activity</h2>
              <Activity className="w-5 h-5 text-orange-primary" />
            </div>
            <ActivityTimeline activities={recentActivities} />
          </div>
        </motion.div>

        {/* System Metrics */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <div className="glass-panel p-6 h-full">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">System Health</h2>
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            </div>
            <SystemMetrics />
          </div>
        </motion.div>
      </div>

      {/* Sidebar */}
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab}
        collapsed={collapsed}
        setCollapsed={setCollapsed}
        chats={chats}
        activeChat={activeChat}
        onChatSelect={handleChatSelect}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
        onRenameChat={handleRenameChat}
      />

      {/* Content */}
      {renderContent()}

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="glass-panel p-6"
      >
        <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
        <div className="flex flex-wrap gap-4">
          <button className="btn-primary">
            Start New Experiment
          </button>
          <button className="btn-secondary">
            Deploy Agent
          </button>
          <button className="btn-secondary">
            Analyze Data
          </button>
          <button className="btn-secondary">
            Generate Report
          </button>
        </div>
      </motion.div>
    </div>
  )
}
