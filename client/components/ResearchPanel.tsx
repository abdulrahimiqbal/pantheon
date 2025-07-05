'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Send, 
  Upload, 
  FileText, 
  Brain, 
  Lightbulb,
  Clock,
  CheckCircle,
  AlertTriangle
} from 'lucide-react'

export default function ResearchPanel() {
  const [inputText, setInputText] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputText.trim()) return
    
    setIsProcessing(true)
    // Simulate processing
    setTimeout(() => {
      setIsProcessing(false)
      setInputText('')
    }, 3000)
  }

  const recentHypotheses = [
    {
      id: 1,
      title: "Quantum Field Fluctuations in Dark Energy",
      status: "validated",
      confidence: 87,
      timestamp: "2 hours ago",
      icon: CheckCircle,
      color: "text-green-400"
    },
    {
      id: 2,
      title: "Modified Gravity at Galactic Scales",
      status: "testing",
      confidence: 72,
      timestamp: "4 hours ago",
      icon: Clock,
      color: "text-yellow-400"
    },
    {
      id: 3,
      title: "Neutrino Mass Hierarchy Resolution",
      status: "needs-review",
      confidence: 65,
      timestamp: "6 hours ago",
      icon: AlertTriangle,
      color: "text-orange-400"
    }
  ]

  return (
    <div className="space-y-6">
      {/* Research Input Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="glass-panel p-6"
      >
        <div className="flex items-center space-x-3 mb-6">
          <Brain className="w-6 h-6 text-purple-primary" />
          <h2 className="text-2xl font-bold text-white">Research Assistant</h2>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-light mb-2">
              Research Query or Hypothesis
            </label>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Enter your research question, hypothesis, or data for analysis..."
              className="w-full h-32 input-field resize-none"
              disabled={isProcessing}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                type="button"
                className="btn-secondary flex items-center space-x-2"
                disabled={isProcessing}
              >
                <Upload className="w-4 h-4" />
                <span>Upload Data</span>
              </button>
              
              <button
                type="button"
                className="btn-secondary flex items-center space-x-2"
                disabled={isProcessing}
              >
                <FileText className="w-4 h-4" />
                <span>Load Template</span>
              </button>
            </div>

            <button
              type="submit"
              disabled={isProcessing || !inputText.trim()}
              className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isProcessing ? (
                <>
                  <div className="loading-dots">
                    <div></div>
                    <div></div>
                    <div></div>
                    <div></div>
                  </div>
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Analyze</span>
                </>
              )}
            </button>
          </div>
        </form>
      </motion.div>

      {/* Results Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Hypotheses */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="glass-panel p-6"
        >
          <div className="flex items-center space-x-3 mb-6">
            <Lightbulb className="w-5 h-5 text-yellow-400" />
            <h3 className="text-xl font-semibold text-white">Recent Hypotheses</h3>
          </div>

          <div className="space-y-4">
            {recentHypotheses.map((hypothesis, index) => {
              const Icon = hypothesis.icon
              
              return (
                <motion.div
                  key={hypothesis.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className="p-4 rounded-lg bg-background-tertiary/50 hover:bg-background-tertiary transition-colors cursor-pointer"
                >
                  <div className="flex items-start space-x-3">
                    <Icon className={`w-5 h-5 ${hypothesis.color} mt-1`} />
                    <div className="flex-1">
                      <h4 className="text-white font-medium mb-1">
                        {hypothesis.title}
                      </h4>
                      <div className="flex items-center space-x-4 text-sm text-gray-medium">
                        <span>Confidence: {hypothesis.confidence}%</span>
                        <span>{hypothesis.timestamp}</span>
                      </div>
                      <div className="mt-2">
                        <div className="w-full bg-background-secondary rounded-full h-1">
                          <div
                            className="h-1 bg-gradient-to-r from-purple-primary to-purple-accent rounded-full"
                            style={{ width: `${hypothesis.confidence}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </motion.div>

        {/* Research Insights */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="glass-panel p-6"
        >
          <div className="flex items-center space-x-3 mb-6">
            <Brain className="w-5 h-5 text-purple-primary" />
            <h3 className="text-xl font-semibold text-white">AI Insights</h3>
          </div>

          <div className="space-y-4">
            <div className="p-4 rounded-lg bg-gradient-to-r from-purple-primary/10 to-purple-accent/10 border border-purple-primary/20">
              <h4 className="text-white font-medium mb-2">Trending Research Areas</h4>
              <ul className="space-y-1 text-sm text-gray-light">
                <li>• Quantum gravity phenomenology</li>
                <li>• Dark matter direct detection</li>
                <li>• Cosmological parameter estimation</li>
              </ul>
            </div>

            <div className="p-4 rounded-lg bg-gradient-to-r from-blue-primary/10 to-blue-accent/10 border border-blue-primary/20">
              <h4 className="text-white font-medium mb-2">Suggested Experiments</h4>
              <ul className="space-y-1 text-sm text-gray-light">
                <li>• High-energy particle collision analysis</li>
                <li>• Gravitational wave data mining</li>
                <li>• Stellar nucleosynthesis modeling</li>
              </ul>
            </div>

            <div className="p-4 rounded-lg bg-gradient-to-r from-green-primary/10 to-green-accent/10 border border-green-primary/20">
              <h4 className="text-white font-medium mb-2">Data Correlations</h4>
              <ul className="space-y-1 text-sm text-gray-light">
                <li>• CMB temperature fluctuations</li>
                <li>• Supernovae luminosity distances</li>
                <li>• Galaxy cluster mass distributions</li>
              </ul>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
