'use client'

import { motion } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { 
  Brain, 
  ExternalLink, 
  BookOpen, 
  Lightbulb, 
  Target,
  TrendingUp,
  BarChart3,
  Atom,
  Calculator,
  Microscope,
  Zap,
  Award,
  Clock
} from 'lucide-react'
import { ScientificProcessingResult } from '../services/gemini'

interface ScientificMessageProps {
  result: ScientificProcessingResult
  timestamp: string
}

const ConfidenceBar = ({ confidence }: { confidence: number }) => {
  const percentage = Math.round(confidence * 100)
  const color = confidence > 0.8 ? 'green' : confidence > 0.6 ? 'yellow' : 'red'
  
  return (
    <div className="flex items-center space-x-2">
      <span className="text-gray-400 text-xs">Confidence:</span>
      <div className="w-16 h-2 bg-black/30 rounded-full overflow-hidden">
        <motion.div
          className={`h-full bg-${color}-500`}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 1, delay: 0.5 }}
        />
      </div>
      <span className={`text-${color}-400 text-xs font-medium`}>{percentage}%</span>
    </div>
  )
}

const MediaCard = ({ media, index }: { media: any, index: number }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="bg-black/30 backdrop-blur-sm border border-orange-primary/20 rounded-lg p-4"
    >
      {media.type === 'simulation' && (
        <div className="space-y-3">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-orange-primary to-orange-accent rounded-lg flex items-center justify-center">
              <Atom className="w-5 h-5 text-white animate-spin" />
            </div>
            <div>
              <h4 className="text-white font-medium">Physics Simulation</h4>
              <p className="text-gray-400 text-sm">Monte Carlo Analysis</p>
            </div>
          </div>
          <div className="bg-black/40 rounded-lg p-3">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Iterations:</span>
                <span className="text-orange-primary ml-2 font-mono">10,000</span>
              </div>
              <div>
                <span className="text-gray-400">Convergence:</span>
                <span className="text-green-400 ml-2 font-mono">99.7%</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {media.type === 'chart' && (
        <div className="space-y-3">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h4 className="text-white font-medium">Statistical Analysis</h4>
              <p className="text-gray-400 text-sm">Correlation Plot</p>
            </div>
          </div>
          <div className="bg-black/40 rounded-lg p-3">
            <div className="h-24 bg-gradient-to-r from-green-500/20 to-blue-500/20 rounded flex items-center justify-center">
              <TrendingUp className="w-8 h-8 text-green-400" />
            </div>
            <div className="mt-2 text-center">
              <span className="text-green-400 font-mono text-sm">R² = 0.94</span>
            </div>
          </div>
        </div>
      )}

      {media.type === 'equation' && (
        <div className="space-y-3">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
              <Calculator className="w-5 h-5 text-white" />
            </div>
            <div>
              <h4 className="text-white font-medium">Mathematical Model</h4>
              <p className="text-gray-400 text-sm">Differential Equations</p>
            </div>
          </div>
          <div className="bg-black/40 rounded-lg p-3 text-center">
            <div className="text-blue-400 font-mono text-lg">
              ∂²ψ/∂t² = c²∇²ψ
            </div>
            <p className="text-gray-400 text-xs mt-1">Wave Equation Solution</p>
          </div>
        </div>
      )}
    </motion.div>
  )
}

export default function ScientificMessage({ result, timestamp }: ScientificMessageProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      {/* Main Response */}
      <div className="flex items-start space-x-3">
        <div className="w-8 h-8 bg-gradient-to-r from-orange-primary to-orange-accent rounded-full flex items-center justify-center flex-shrink-0">
          <Brain className="w-4 h-4 text-white" />
        </div>
        <div className="flex-1">
          <div className="bg-black/20 border border-white/10 backdrop-blur-sm rounded-2xl p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Award className="w-4 h-4 text-orange-primary" />
                <span className="text-orange-primary font-medium text-sm">Scientific Analysis Complete</span>
              </div>
              <div className="flex items-center space-x-2 text-gray-400 text-xs">
                <Clock className="w-3 h-3" />
                <span>{timestamp}</span>
              </div>
            </div>
            
            <div className="prose prose-invert max-w-none text-gray-light leading-relaxed">
              <ReactMarkdown 
                remarkPlugins={[remarkGfm]}
                components={{
                  // Custom styling for markdown elements
                  h1: ({children}) => <h1 className="text-xl font-bold text-white mb-3">{children}</h1>,
                  h2: ({children}) => <h2 className="text-lg font-semibold text-white mb-2">{children}</h2>,
                  h3: ({children}) => <h3 className="text-base font-medium text-white mb-2">{children}</h3>,
                  p: ({children}) => <p className="text-gray-light mb-3 leading-relaxed">{children}</p>,
                  ul: ({children}) => <ul className="list-disc list-inside text-gray-light mb-3 space-y-1">{children}</ul>,
                  ol: ({children}) => <ol className="list-decimal list-inside text-gray-light mb-3 space-y-1">{children}</ol>,
                  li: ({children}) => <li className="text-gray-light">{children}</li>,
                  strong: ({children}) => <strong className="text-white font-semibold">{children}</strong>,
                  em: ({children}) => <em className="text-orange-primary italic">{children}</em>,
                  code: ({children}) => <code className="bg-black/40 text-orange-accent px-1 py-0.5 rounded text-sm font-mono">{children}</code>,
                  pre: ({children}) => <pre className="bg-black/40 border border-white/10 rounded-lg p-3 overflow-x-auto mb-3">{children}</pre>,
                  blockquote: ({children}) => <blockquote className="border-l-4 border-orange-primary pl-4 italic text-gray-300 mb-3">{children}</blockquote>,
                  a: ({href, children}) => <a href={href} className="text-orange-primary hover:text-orange-accent underline" target="_blank" rel="noopener noreferrer">{children}</a>,
                  table: ({children}) => <table className="w-full border-collapse border border-white/20 mb-3">{children}</table>,
                  th: ({children}) => <th className="border border-white/20 px-3 py-2 bg-black/20 text-white font-medium text-left">{children}</th>,
                  td: ({children}) => <td className="border border-white/20 px-3 py-2 text-gray-light">{children}</td>,
                }}
              >
                {result.response}
              </ReactMarkdown>
            </div>

            {/* Confidence and Metrics */}
            <div className="mt-4 pt-3 border-t border-white/10">
              <ConfidenceBar confidence={result.confidence} />
            </div>
          </div>
        </div>
      </div>

      {/* Media Visualizations */}
      {result.thinkingSteps.some(step => step.media) && (
        <div className="ml-11 space-y-3">
          <h4 className="text-white font-medium text-sm flex items-center space-x-2">
            <Microscope className="w-4 h-4 text-orange-primary" />
            <span>Scientific Visualizations</span>
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {result.thinkingSteps
              .filter(step => step.media)
              .flatMap(step => step.media || [])
              .map((media, index) => (
                <MediaCard key={index} media={media} index={index} />
              ))}
          </div>
        </div>
      )}

      {/* Sources */}
      {result.sources.length > 0 && (
        <div className="ml-11">
          <h4 className="text-white font-medium text-sm mb-3 flex items-center space-x-2">
            <BookOpen className="w-4 h-4 text-blue-400" />
            <span>Scientific Sources</span>
          </h4>
          <div className="space-y-2">
            {result.sources.slice(0, 3).map((source, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-start space-x-3 p-3 bg-black/20 backdrop-blur-sm rounded-lg border border-blue-400/20"
              >
                <ExternalLink className="w-3 h-3 text-blue-400 flex-shrink-0" />
                <div className="text-blue-400 text-sm flex-1 min-w-0 break-words">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      p: ({ children }) => <p className="mb-1 last:mb-0">{children}</p>,
                      strong: ({ children }) => <strong className="text-blue-300 font-semibold">{children}</strong>,
                      em: ({ children }) => <em className="text-blue-300 italic">{children}</em>,
                      code: ({ children }) => (
                        <code className="bg-blue-400/10 text-blue-300 px-1 py-0.5 rounded text-xs font-mono">
                          {children}
                        </code>
                      ),
                      a: ({ href, children }) => (
                        <a 
                          href={href} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-300 hover:text-blue-200 underline transition-colors"
                        >
                          {children}
                        </a>
                      )
                    }}
                  >
                    {source}
                  </ReactMarkdown>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Related Concepts */}
      {result.relatedConcepts.length > 0 && (
        <div className="ml-11">
          <h4 className="text-white font-medium text-sm mb-3 flex items-center space-x-2">
            <Lightbulb className="w-4 h-4 text-yellow-400" />
            <span>Related Concepts</span>
          </h4>
          <div className="space-y-2">
            {result.relatedConcepts.map((concept, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-3 bg-yellow-400/10 border border-yellow-400/30 rounded-lg"
              >
                <div className="text-yellow-400 text-sm break-words">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      p: ({ children }) => <p className="mb-1 last:mb-0">{children}</p>,
                      strong: ({ children }) => <strong className="text-yellow-300 font-semibold">{children}</strong>,
                      em: ({ children }) => <em className="text-yellow-300 italic">{children}</em>,
                      code: ({ children }) => (
                        <code className="bg-yellow-400/10 text-yellow-300 px-1 py-0.5 rounded text-xs font-mono">
                          {children}
                        </code>
                      ),
                      a: ({ href, children }) => (
                        <a 
                          href={href} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-yellow-300 hover:text-yellow-200 underline transition-colors"
                        >
                          {children}
                        </a>
                      )
                    }}
                  >
                    {concept}
                  </ReactMarkdown>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Suggested Experiments */}
      {result.suggestedExperiments.length > 0 && (
        <div className="ml-11">
          <h4 className="text-white font-medium text-sm mb-3 flex items-center space-x-2">
            <Target className="w-4 h-4 text-green-400" />
            <span>Suggested Experiments</span>
          </h4>
          <div className="space-y-2">
            {result.suggestedExperiments.slice(0, 3).map((experiment, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-start space-x-3 p-3 bg-black/20 backdrop-blur-sm rounded-lg border border-green-400/20"
              >
                <Zap className="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" />
                <div className="text-green-400 text-sm flex-1 min-w-0 break-words">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                      strong: ({ children }) => <strong className="text-green-300 font-semibold">{children}</strong>,
                      em: ({ children }) => <em className="text-green-300 italic">{children}</em>,
                      code: ({ children }) => (
                        <code className="bg-green-400/10 text-green-300 px-1 py-0.5 rounded text-xs font-mono">
                          {children}
                        </code>
                      ),
                      ul: ({ children }) => <ul className="list-disc list-inside space-y-1 ml-2">{children}</ul>,
                      ol: ({ children }) => <ol className="list-decimal list-inside space-y-1 ml-2">{children}</ol>,
                      li: ({ children }) => <li className="text-green-400">{children}</li>,
                      a: ({ href, children }) => (
                        <a 
                          href={href} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-green-300 hover:text-green-200 underline transition-colors"
                        >
                          {children}
                        </a>
                      )
                    }}
                  >
                    {experiment}
                  </ReactMarkdown>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  )
}
