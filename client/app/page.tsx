'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'
import ResearchPanel from '@/components/ResearchPanel'
import VisualizationPanel from '@/components/VisualizationPanel'
import ConfigPanel from '@/components/ConfigPanel'
import { ScientificProcessingResult } from '@/services/gemini'
// import CursorEffect from '@/components/CursorEffect'

interface Chat {
  id: string
  name: string
  lastMessage: string
  timestamp: string
}

interface Message {
  id: string
  text: string
  type: 'user' | 'assistant' | 'scientific'
  timestamp: string
  scientificResult?: ScientificProcessingResult
}

export default function Home() {
  const [activeTab, setActiveTab] = useState('chat')
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [chats, setChats] = useState<Chat[]>([])
  const [activeChat, setActiveChat] = useState<string | null>(null)
  const [messages, setMessages] = useState<{ [chatId: string]: Message[] }>({})

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

  // Generate AI response based on user input
  const generateAIResponse = async (messageText: string): Promise<string> => {
    // This is where you would integrate with your actual AI backend
    // For now, providing more realistic physics-focused responses
    
    const responses = [
      `Regarding "${messageText}", this touches on fundamental principles in theoretical physics. Let me break down the key concepts and their implications for current research.`,
      `That's an excellent question about "${messageText}". In the context of modern physics, this relates to several cutting-edge areas of study including quantum mechanics and relativity.`,
      `Your inquiry about "${messageText}" is particularly relevant to current research in particle physics and cosmology. Here's what the latest findings suggest...`,
      `The topic of "${messageText}" intersects with some fascinating areas of physics research. Let me explain the theoretical framework and experimental evidence.`,
      `"${messageText}" is a complex subject that involves multiple branches of physics. The current scientific consensus and ongoing research directions are quite intriguing.`
    ]
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000))
    
    return responses[Math.floor(Math.random() * responses.length)]
  }

  const handleSendMessage = async (chatId: string, messageText: string, scientificResult?: ScientificProcessingResult) => {
    // Handle both regular messages and scientific results
    if (scientificResult) {
      // This is a scientific AI response
      const scientificMessage: Message = {
        id: generateMessageId(),
        text: scientificResult.response,
        type: 'scientific',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        scientificResult: scientificResult
      }
      
      setMessages(prev => ({
        ...prev,
        [chatId]: [...(prev[chatId] || []), scientificMessage]
      }))
      
      // Update chat's last message
      setChats(prev => prev.map(chat => 
        chat.id === chatId 
          ? { ...chat, lastMessage: 'Scientific analysis complete', timestamp: scientificMessage.timestamp }
          : chat
      ))
      
      return
    }
    
    // Regular user message
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
    
    // Generate AI response (only for regular messages, scientific responses are handled in ResearchPanel)
    try {
      const aiResponseText = await generateAIResponse(messageText)
      const aiMessage: Message = {
        id: generateMessageId(),
        text: aiResponseText,
        type: 'assistant',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
      
      setMessages(prev => ({
        ...prev,
        [chatId]: [...(prev[chatId] || []), aiMessage]
      }))
      
      // Update chat's last message with AI response
      setChats(prev => prev.map(chat => 
        chat.id === chatId 
          ? { ...chat, lastMessage: aiMessage.text.substring(0, 50) + (aiMessage.text.length > 50 ? '...' : ''), timestamp: aiMessage.timestamp }
          : chat
      ))
    } catch (error) {
      console.error('Failed to generate AI response:', error)
    }
  }

  // Function to get AI response for voice chat
  const getAIResponse = async (messageText: string): Promise<string> => {
    return await generateAIResponse(messageText)
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'chat':
        return (
          <ResearchPanel 
            activeChat={activeChat}
            messages={messages}
            onSendMessage={handleSendMessage}
            onGetAIResponse={getAIResponse}
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
            onGetAIResponse={getAIResponse}
          />
        )
    }
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab}
        collapsed={sidebarCollapsed}
        setCollapsed={setSidebarCollapsed}
        chats={chats}
        activeChat={activeChat}
        onChatSelect={handleChatSelect}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
        onRenameChat={handleRenameChat}
      />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-auto p-6">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="h-full"
          >
            {renderContent()}
          </motion.div>
        </main>
      </div>
      
      {/* Custom Cursor Effect - Disabled */}
      {/* <CursorEffect /> */}
    </div>
  )
}
