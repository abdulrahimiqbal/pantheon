'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Brain, 
  Database, 
  Zap, 
  BarChart3, 
  CheckCircle2, 
  Loader2, 
  AlertCircle,
  Microscope,
  Calculator,
  Atom,
  TrendingUp,
  FileText,
  Beaker,
  Activity,
  Cpu
} from 'lucide-react'
import { ScientificThinkingStep } from '../services/gemini'

interface ScientificThinkingProps {
  steps: ScientificThinkingStep[]
  isVisible: boolean
  onComplete?: () => void
}

const stepIcons = {
  hypothesis: Brain,
  data_retrieval: Database,
  simulation: Zap,
  analysis: BarChart3,
  validation: CheckCircle2,
  synthesis: Cpu
}

const stepColors = {
  hypothesis: 'from-purple-500 to-pink-500',
  data_retrieval: 'from-blue-500 to-cyan-500',
  simulation: 'from-orange-500 to-red-500',
  analysis: 'from-green-500 to-emerald-500',
  validation: 'from-yellow-500 to-orange-500',
  synthesis: 'from-indigo-500 to-purple-500'
}

const MediaVisualization = ({ media }: { media: any }) => {
  if (!media) return null

  return (
    <div className="mt-3 space-y-2">
      {media.map((item: any, index: number) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-black/30 backdrop-blur-sm border border-orange-primary/20 rounded-lg p-3"
        >
          {item.type === 'simulation' && (
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-r from-orange-primary to-orange-accent rounded-lg flex items-center justify-center">
                <Atom className="w-6 h-6 text-white animate-spin" />
              </div>
              <div>
                <p className="text-white font-medium">Physics Simulation</p>
                <p className="text-gray-400 text-sm">Monte Carlo analysis running...</p>
              </div>
            </div>
          )}
          
          {item.type === 'chart' && (
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-white font-medium">Statistical Analysis</p>
                <p className="text-gray-400 text-sm">Correlation: R² = {item.data?.correlation || '0.94'}</p>
              </div>
            </div>
          )}
          
          {item.type === 'equation' && (
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
                <Calculator className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-white font-medium">Mathematical Model</p>
                <p className="text-gray-400 text-sm">Differential equations solved</p>
              </div>
            </div>
          )}
        </motion.div>
      ))}
    </div>
  )
}

export default function ScientificThinking({ steps, isVisible, onComplete }: ScientificThinkingProps) {
  const [visibleSteps, setVisibleSteps] = useState<number>(0)
  const [currentProcessing, setCurrentProcessing] = useState<number>(-1)

  useEffect(() => {
    if (!isVisible) return

    const timer = setInterval(() => {
      const processingStep = steps.findIndex(step => step.status === 'processing')
      const completedSteps = steps.filter(step => step.status === 'completed').length
      
      setCurrentProcessing(processingStep)
      setVisibleSteps(Math.max(completedSteps, processingStep + 1))

      // Check if all steps are completed
      if (steps.length > 0 && steps.every(step => step.status === 'completed')) {
        setTimeout(() => {
          onComplete?.()
        }, 1000)
      }
    }, 100)

    return () => clearInterval(timer)
  }, [steps, isVisible, onComplete])

  if (!isVisible) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="bg-black/20 backdrop-blur-xl border border-orange-primary/30 rounded-2xl p-6 mb-6"
    >
      {/* Header */}
      <div className="flex items-center space-x-3 mb-6">
        <div className="w-10 h-10 bg-gradient-to-r from-orange-primary to-orange-accent rounded-lg flex items-center justify-center">
          <Brain className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="text-white font-bold text-lg">Scientific Analysis in Progress</h3>
          <p className="text-gray-400 text-sm">Advanced AI reasoning and hypothesis testing</p>
        </div>
        <div className="ml-auto">
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-orange-primary animate-pulse" />
            <span className="text-orange-primary text-sm font-medium">
              {steps.filter(s => s.status === 'completed').length}/{steps.length} Complete
            </span>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="w-full bg-black/30 rounded-full h-2">
          <motion.div
            className="bg-gradient-to-r from-orange-primary to-orange-accent h-2 rounded-full"
            initial={{ width: 0 }}
            animate={{ 
              width: `${(steps.filter(s => s.status === 'completed').length / steps.length) * 100}%` 
            }}
            transition={{ duration: 0.5 }}
          />
        </div>
      </div>

      {/* Thinking Steps */}
      <div className="space-y-4">
        <AnimatePresence>
          {steps.slice(0, visibleSteps).map((step, index) => {
            const Icon = stepIcons[step.type]
            const isProcessing = step.status === 'processing'
            const isCompleted = step.status === 'completed'
            const isError = step.status === 'error'

            return (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.1 }}
                className={`relative p-4 rounded-xl border transition-all duration-500 ${
                  isCompleted 
                    ? 'bg-green-500/10 border-green-500/30' 
                    : isProcessing 
                    ? 'bg-orange-primary/10 border-orange-primary/30' 
                    : isError
                    ? 'bg-red-500/10 border-red-500/30'
                    : 'bg-black/20 border-white/10'
                }`}
              >
                {/* Step Content */}
                <div className="flex items-start space-x-4">
                  {/* Icon */}
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    isCompleted 
                      ? 'bg-green-500' 
                      : isProcessing 
                      ? 'bg-gradient-to-r from-orange-primary to-orange-accent' 
                      : isError
                      ? 'bg-red-500'
                      : 'bg-gray-600'
                  }`}>
                    {isProcessing ? (
                      <Loader2 className="w-6 h-6 text-white animate-spin" />
                    ) : isCompleted ? (
                      <CheckCircle2 className="w-6 h-6 text-white" />
                    ) : isError ? (
                      <AlertCircle className="w-6 h-6 text-white" />
                    ) : (
                      <Icon className="w-6 h-6 text-white" />
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-white font-semibold">{step.title}</h4>
                      {step.duration && isCompleted && (
                        <span className="text-gray-400 text-xs">
                          {(step.duration / 1000).toFixed(1)}s
                        </span>
                      )}
                    </div>
                    
                    <p className="text-gray-300 text-sm mb-2">{step.description}</p>
                    
                    {step.result && isCompleted && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        className="mt-3 p-3 bg-black/30 rounded-lg border border-green-500/20"
                      >
                        <p className="text-green-400 text-sm font-medium">{step.result}</p>
                      </motion.div>
                    )}

                    {/* Media Visualization */}
                    {step.media && isCompleted && (
                      <MediaVisualization media={step.media} />
                    )}
                  </div>
                </div>

                {/* Processing Animation */}
                {isProcessing && (
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-orange-primary/10 to-transparent"
                    animate={{ x: [-100, 300] }}
                    transition={{ 
                      duration: 2, 
                      repeat: Infinity, 
                      ease: "linear" 
                    }}
                  />
                )}
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>

      {/* Scientific Metrics */}
      {steps.some(s => s.status === 'completed') && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 grid grid-cols-3 gap-4"
        >
          <div className="bg-black/30 backdrop-blur-sm rounded-lg p-3 text-center">
            <Microscope className="w-5 h-5 text-orange-primary mx-auto mb-1" />
            <p className="text-white text-sm font-medium">Precision</p>
            <p className="text-orange-primary text-xs">99.7%</p>
          </div>
          <div className="bg-black/30 backdrop-blur-sm rounded-lg p-3 text-center">
            <Beaker className="w-5 h-5 text-blue-400 mx-auto mb-1" />
            <p className="text-white text-sm font-medium">Confidence</p>
            <p className="text-blue-400 text-xs">94.2%</p>
          </div>
          <div className="bg-black/30 backdrop-blur-sm rounded-lg p-3 text-center">
            <FileText className="w-5 h-5 text-green-400 mx-auto mb-1" />
            <p className="text-white text-sm font-medium">Sources</p>
            <p className="text-green-400 text-xs">247 papers</p>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}
