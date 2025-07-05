'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Send, 
  Upload, 
  Brain,
  Mic
} from 'lucide-react'
import VoiceChat from './VoiceChat'

interface Message {
  id: string
  text: string
  type: 'user' | 'assistant'
  timestamp: string
}

interface ResearchPanelProps {
  activeChat: string | null
  messages: { [chatId: string]: Message[] }
  onSendMessage: (chatId: string, message: string) => void
  onGetAIResponse?: (message: string) => Promise<string>
}

export default function ResearchPanel({ activeChat, messages, onSendMessage, onGetAIResponse }: ResearchPanelProps) {
  const [inputText, setInputText] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [showVoiceChat, setShowVoiceChat] = useState(false)
  
  const currentMessages = activeChat ? messages[activeChat] || [] : []

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputText.trim() || !activeChat) return
    
    setIsProcessing(true)
    onSendMessage(activeChat, inputText.trim())
    setInputText('')
    
    // Simulate AI response
    setTimeout(() => {
      setIsProcessing(false)
    }, 2000)
  }

  return (
    <div className="h-full flex flex-col bg-background-primary">
      {/* Header */}
      <div className="p-6 border-b border-orange-primary/20">
        <div className="flex items-center space-x-3">
          <Brain className="w-6 h-6 text-orange-primary" />
          <h2 className="text-2xl font-bold text-white">Research Assistant</h2>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {!activeChat ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <Brain className="w-16 h-16 text-orange-primary mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Welcome to Pantheon AI</h3>
              <p className="text-gray-medium mb-4">Select a chat or create a new one to start your research conversation</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {currentMessages.length === 0 ? (
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-orange-primary to-orange-accent rounded-full flex items-center justify-center flex-shrink-0">
                  <Brain className="w-4 h-4 text-white" />
                </div>
                <div className="flex-1">
                  <p className="text-gray-light leading-relaxed">
                    Welcome to Pantheon AI Research Assistant. I'm here to help you explore complex physics concepts, 
                    validate hypotheses, and accelerate your research. What would you like to investigate today?
                  </p>
                </div>
              </div>
            ) : (
              currentMessages.map((message) => (
                <div key={message.id} className={`flex items-start space-x-3 ${
                  message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                }`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    message.type === 'user' 
                      ? 'bg-background-tertiary' 
                      : 'bg-gradient-to-r from-orange-primary to-orange-accent'
                  }`}>
                    {message.type === 'user' ? (
                      <div className="w-4 h-4 bg-gray-medium rounded-full" />
                    ) : (
                      <Brain className="w-4 h-4 text-white" />
                    )}
                  </div>
                  <div className={`flex-1 ${
                    message.type === 'user' ? 'text-right' : ''
                  }`}>
                    <div className={`inline-block p-3 rounded-lg max-w-[80%] ${
                      message.type === 'user'
                        ? 'bg-orange-primary/20 text-white'
                        : 'bg-background-secondary text-gray-light'
                    }`}>
                      <p className="leading-relaxed">{message.text}</p>
                    </div>
                    <p className="text-xs text-gray-medium mt-1">{message.timestamp}</p>
                  </div>
                </div>
              ))
            )}
            
            {isProcessing && (
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-orange-primary to-orange-accent rounded-full flex items-center justify-center flex-shrink-0">
                  <Brain className="w-4 h-4 text-white animate-pulse" />
                </div>
                <div className="flex-1">
                  <div className="bg-background-secondary p-3 rounded-lg">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-orange-primary rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-orange-primary rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                      <div className="w-2 h-2 bg-orange-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-6 border-t border-orange-primary/20">
        {activeChat ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="flex space-x-3">
              <div className="flex-1">
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Ask about quantum mechanics, relativity, particle physics, or any research question..."
                  className="w-full h-20 p-4 bg-background-secondary border border-orange-primary/30 rounded-lg text-white placeholder-gray-medium resize-none focus:outline-none focus:border-orange-primary focus:ring-2 focus:ring-orange-primary/20 transition-all duration-200"
                  disabled={isProcessing}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      handleSubmit(e)
                    }
                  }}
                />
              </div>
              <div className="flex flex-col space-y-2">
                <button
                  type="submit"
                  disabled={!inputText.trim() || isProcessing}
                  className="p-3 bg-gradient-to-r from-orange-primary to-orange-accent text-white rounded-lg hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                >
                  {isProcessing ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    >
                      <Brain className="w-5 h-5" />
                    </motion.div>
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </button>
                <button
                  type="button"
                  className="p-3 bg-background-tertiary text-gray-medium rounded-lg hover:text-white hover:bg-background-secondary transition-all duration-200"
                  title="Upload file"
                >
                  <Upload className="w-5 h-5" />
                </button>
                <button
                  type="button"
                  onClick={() => setShowVoiceChat(!showVoiceChat)}
                  className={`p-3 rounded-lg transition-all duration-200 ${
                    showVoiceChat 
                      ? 'bg-gradient-to-r from-orange-primary to-orange-accent text-white shadow-lg' 
                      : 'bg-background-tertiary text-gray-medium hover:text-white hover:bg-background-secondary'
                  }`}
                  title="Voice Chat"
                >
                  <Mic className="w-5 h-5" />
                </button>
              </div>
            </div>
          </form>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-medium">Select or create a chat to start your research conversation</p>
          </div>
        )}  
      </div>
      
      {/* Voice Chat Modal */}
      {showVoiceChat && (
        <VoiceChat
          isOpen={showVoiceChat}
          onClose={() => setShowVoiceChat(false)}
          onSendMessage={(message: string) => {
            if (activeChat) {
              onSendMessage(activeChat, message)
            }
          }}
          onGetAIResponse={onGetAIResponse}
        />
      )}
    </div>
  )
}
