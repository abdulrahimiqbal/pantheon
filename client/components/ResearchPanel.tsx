'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Send, 
  Upload, 
  Brain,
  Mic,
  Sparkles,
  Zap,
  Activity
} from 'lucide-react'
import VoiceChat from './VoiceChat'
import ScientificThinking from './ScientificThinking'
import ScientificMessage from './ScientificMessage'
import { geminiService, ScientificThinkingStep, ScientificProcessingResult } from '../services/gemini'

interface Message {
  id: string
  text: string
  type: 'user' | 'assistant' | 'scientific'
  timestamp: string
  scientificResult?: ScientificProcessingResult
}

interface ResearchPanelProps {
  activeChat: string | null
  messages: { [chatId: string]: Message[] }
  onSendMessage: (chatId: string, message: string, scientificResult?: ScientificProcessingResult) => void
  onGetAIResponse?: (message: string) => Promise<string>
}

export default function ResearchPanel({ activeChat, messages, onSendMessage, onGetAIResponse }: ResearchPanelProps) {
  const [inputText, setInputText] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [showVoiceChat, setShowVoiceChat] = useState(false)
  const [isScientificMode, setIsScientificMode] = useState(true)
  const [currentThinkingSteps, setCurrentThinkingSteps] = useState<ScientificThinkingStep[]>([])
  const [showThinking, setShowThinking] = useState(false)

  // Scientific processing function for voice chat
  const handleScientificVoiceQuery = async (message: string): Promise<ScientificProcessingResult> => {
    return await geminiService.processScientificQuery(message)
  }
  const [processingStatus, setProcessingStatus] = useState<string>('')
  
  const currentMessages = activeChat ? messages[activeChat] || [] : []

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputText.trim() || !activeChat || isProcessing) return
    
    const userMessage = inputText.trim()
    setInputText('')
    setIsProcessing(true)
    setShowThinking(isScientificMode)
    
    // Send user message
    onSendMessage(activeChat, userMessage)
    
    try {
      if (isScientificMode) {
        // Use scientific AI processing
        setProcessingStatus('Initializing scientific analysis...')
        
        const result = await geminiService.processScientificQuery(
          userMessage,
          (steps) => {
            setCurrentThinkingSteps([...steps])
          }
        )
        
        // Send scientific result to parent
        onSendMessage(activeChat, result.response, result)
        
      } else {
        // Use regular AI response
        if (onGetAIResponse) {
          const response = await onGetAIResponse(userMessage)
          // Response is handled by parent component
        }
      }
    } catch (error) {
      console.error('AI processing error:', error)
      setProcessingStatus('Error processing request. Please try again.')
    } finally {
      setIsProcessing(false)
      setShowThinking(false)
      setProcessingStatus('')
      setTimeout(() => {
        setCurrentThinkingSteps([])
      }, 1000)
    }
  }

  return (
    <div className="h-full flex flex-col bg-background-primary">
      {/* Header */}
      <div className="p-6 border-b border-orange-primary/20 bg-black/10 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-orange-primary to-orange-accent rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Pantheon AI Research</h2>
              <p className="text-gray-400 text-sm">Advanced Scientific Analysis</p>
            </div>
          </div>
          
          {/* AI Mode Toggle */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <span className="text-gray-400 text-sm">Mode:</span>
              <button
                onClick={() => setIsScientificMode(!isScientificMode)}
                className={`px-4 py-2 rounded-lg border transition-all duration-200 flex items-center space-x-2 ${
                  isScientificMode
                    ? 'bg-orange-primary/20 border-orange-primary/50 text-orange-primary'
                    : 'bg-black/20 border-white/20 text-gray-400 hover:border-orange-primary/30'
                }`}
              >
                {isScientificMode ? (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Scientific AI</span>
                  </>
                ) : (
                  <>
                    <Brain className="w-4 h-4" />
                    <span>Standard AI</span>
                  </>
                )}
              </button>
            </div>
            
            {isProcessing && (
              <div className="flex items-center space-x-2 text-orange-primary">
                <Activity className="w-4 h-4 animate-pulse" />
                <span className="text-sm">{processingStatus || 'Processing...'}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Scientific Thinking Display */}
        <AnimatePresence>
          {showThinking && (
            <ScientificThinking
              steps={currentThinkingSteps}
              isVisible={showThinking}
              onComplete={() => setShowThinking(false)}
            />
          )}
        </AnimatePresence>
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
                <div key={message.id}>
                  {message.type === 'scientific' && message.scientificResult ? (
                    <ScientificMessage 
                      result={message.scientificResult} 
                      timestamp={message.timestamp}
                    />
                  ) : (
                    <div className={`flex items-start space-x-3 ${
                      message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                    }`}>
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                        message.type === 'user' 
                          ? 'bg-orange-primary/20 border-orange-primary/30 backdrop-blur-sm' 
                          : 'bg-gradient-to-r from-orange-primary to-orange-accent'
                      }`}>
                        {message.type === 'user' ? (
                          <div className="w-4 h-4 bg-orange-primary rounded-full" />
                        ) : (
                          <Brain className="w-4 h-4 text-white" />
                        )}
                      </div>
                      <div className={`flex-1 ${
                        message.type === 'user' ? 'text-right' : ''
                      }`}>
                        <div className={`inline-block p-4 rounded-2xl max-w-2xl border backdrop-blur-sm ${
                          message.type === 'user'
                            ? 'bg-orange-primary/20 border-orange-primary/30 text-white'
                            : 'bg-black/20 border-white/10 text-gray-light'
                        }`}>
                          <p className="leading-relaxed whitespace-pre-wrap">{message.text}</p>
                          <div className="flex items-center justify-between mt-2">
                            <p className="text-xs text-gray-medium">{message.timestamp}</p>
                            {message.type === 'assistant' && isScientificMode && (
                              <div className="flex items-center space-x-1 text-orange-primary">
                                <Zap className="w-3 h-3" />
                                <span className="text-xs">AI Enhanced</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
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
      <div className="p-6 border-t border-orange-primary/20 bg-black/10 backdrop-blur-sm">
        {activeChat ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="flex space-x-4">
              <div className="flex-1">
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder={isScientificMode 
                    ? "Ask me complex scientific questions for advanced AI analysis with thinking steps..."
                    : "Ask me anything about physics, research, or scientific concepts..."
                  }
                  className="w-full p-4 bg-black/20 backdrop-blur-sm border border-white/20 rounded-xl text-white placeholder-gray-medium resize-none focus:outline-none focus:border-orange-primary transition-colors"
                  rows={3}
                  disabled={isProcessing}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                      handleSubmit(e)
                    }
                  }}
                />
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex space-x-3">
                <button
                  type="button"
                  className="flex items-center space-x-2 px-4 py-2 bg-black/20 backdrop-blur-sm border border-white/20 rounded-lg text-gray-light hover:border-orange-primary/50 transition-colors"
                  disabled={isProcessing}
                >
                  <Upload className="w-4 h-4" />
                  <span>Upload Data</span>
                </button>
                
                <button
                  type="button"
                  onClick={() => setShowVoiceChat(true)}
                  className="flex items-center space-x-2 px-4 py-2 bg-black/20 backdrop-blur-sm border border-white/20 rounded-lg text-gray-light hover:border-orange-primary/50 transition-colors"
                  disabled={isProcessing}
                >
                  <Mic className="w-4 h-4" />
                  <span>Voice Chat</span>
                </button>
                
                {isScientificMode && (
                  <div className="flex items-center space-x-2 px-3 py-2 bg-orange-primary/10 border border-orange-primary/30 rounded-lg">
                    <Sparkles className="w-4 h-4 text-orange-primary" />
                    <span className="text-orange-primary text-sm font-medium">Scientific Mode</span>
                  </div>
                )}
              </div>
              
              <button
                type="submit"
                disabled={!inputText.trim() || isProcessing}
                className="flex items-center space-x-2 px-6 py-2 bg-gradient-to-r from-orange-primary to-orange-accent hover:from-orange-accent hover:to-orange-primary disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed rounded-lg text-white font-medium transition-all duration-200 shadow-lg hover:shadow-orange-primary/25"
              >
                {isProcessing ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    {isScientificMode ? <Zap className="w-4 h-4" /> : <Send className="w-4 h-4" />}
                    <span>{isScientificMode ? 'Analyze' : 'Send'}</span>
                    <span className="text-xs opacity-70">(⌘↵)</span>
                  </>
                )}
              </button>
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
          onGetScientificResponse={handleScientificVoiceQuery}
        />
      )}
    </div>
  )
}
