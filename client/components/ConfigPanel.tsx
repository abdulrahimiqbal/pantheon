'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Settings, 
  Sliders, 
  Brain, 
  Database,
  Zap,
  Shield,
  Save,
  RotateCcw,
  AlertCircle,
  CheckCircle
} from 'lucide-react'

export default function ConfigPanel() {
  const [config, setConfig] = useState({
    // AI Model Settings
    modelTemperature: 0.7,
    maxTokens: 2048,
    topP: 0.9,
    frequencyPenalty: 0.0,
    
    // System Settings
    maxAgents: 12,
    processingTimeout: 300,
    dataRetention: 30,
    autoSave: true,
    
    // Security Settings
    encryptionEnabled: true,
    auditLogging: true,
    accessControl: 'strict',
    
    // Performance Settings
    batchSize: 32,
    parallelProcessing: true,
    cacheEnabled: true,
    optimizationLevel: 'balanced'
  })

  const [hasChanges, setHasChanges] = useState(false)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')

  const handleConfigChange = (key: string, value: any) => {
    setConfig(prev => ({ ...prev, [key]: value }))
    setHasChanges(true)
    setSaveStatus('idle')
  }

  const handleSave = async () => {
    setSaveStatus('saving')
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    setSaveStatus('saved')
    setHasChanges(false)
    setTimeout(() => setSaveStatus('idle'), 3000)
  }

  const handleReset = () => {
    // Reset to default values
    setConfig({
      modelTemperature: 0.7,
      maxTokens: 2048,
      topP: 0.9,
      frequencyPenalty: 0.0,
      maxAgents: 12,
      processingTimeout: 300,
      dataRetention: 30,
      autoSave: true,
      encryptionEnabled: true,
      auditLogging: true,
      accessControl: 'strict',
      batchSize: 32,
      parallelProcessing: true,
      cacheEnabled: true,
      optimizationLevel: 'balanced'
    })
    setHasChanges(false)
    setSaveStatus('idle')
  }

  const configSections = [
    {
      title: 'AI Model Configuration',
      icon: Brain,
      color: 'text-purple-primary',
      settings: [
        {
          key: 'modelTemperature',
          label: 'Model Temperature',
          type: 'slider',
          min: 0,
          max: 2,
          step: 0.1,
          description: 'Controls randomness in AI responses'
        },
        {
          key: 'maxTokens',
          label: 'Max Tokens',
          type: 'number',
          min: 100,
          max: 4096,
          description: 'Maximum length of AI responses'
        },
        {
          key: 'topP',
          label: 'Top P',
          type: 'slider',
          min: 0,
          max: 1,
          step: 0.1,
          description: 'Nucleus sampling parameter'
        },
        {
          key: 'frequencyPenalty',
          label: 'Frequency Penalty',
          type: 'slider',
          min: -2,
          max: 2,
          step: 0.1,
          description: 'Reduces repetition in responses'
        }
      ]
    },
    {
      title: 'System Configuration',
      icon: Settings,
      color: 'text-blue-400',
      settings: [
        {
          key: 'maxAgents',
          label: 'Maximum Agents',
          type: 'number',
          min: 1,
          max: 50,
          description: 'Maximum number of concurrent agents'
        },
        {
          key: 'processingTimeout',
          label: 'Processing Timeout (seconds)',
          type: 'number',
          min: 30,
          max: 3600,
          description: 'Maximum time for processing tasks'
        },
        {
          key: 'dataRetention',
          label: 'Data Retention (days)',
          type: 'number',
          min: 1,
          max: 365,
          description: 'How long to keep experiment data'
        },
        {
          key: 'autoSave',
          label: 'Auto Save',
          type: 'toggle',
          description: 'Automatically save work progress'
        }
      ]
    },
    {
      title: 'Security Settings',
      icon: Shield,
      color: 'text-green-400',
      settings: [
        {
          key: 'encryptionEnabled',
          label: 'Data Encryption',
          type: 'toggle',
          description: 'Encrypt sensitive data at rest'
        },
        {
          key: 'auditLogging',
          label: 'Audit Logging',
          type: 'toggle',
          description: 'Log all system activities'
        },
        {
          key: 'accessControl',
          label: 'Access Control',
          type: 'select',
          options: ['permissive', 'balanced', 'strict'],
          description: 'Level of access restrictions'
        }
      ]
    },
    {
      title: 'Performance Settings',
      icon: Zap,
      color: 'text-yellow-400',
      settings: [
        {
          key: 'batchSize',
          label: 'Batch Size',
          type: 'number',
          min: 1,
          max: 128,
          description: 'Number of items processed together'
        },
        {
          key: 'parallelProcessing',
          label: 'Parallel Processing',
          type: 'toggle',
          description: 'Enable multi-threaded processing'
        },
        {
          key: 'cacheEnabled',
          label: 'Caching',
          type: 'toggle',
          description: 'Cache frequently accessed data'
        },
        {
          key: 'optimizationLevel',
          label: 'Optimization Level',
          type: 'select',
          options: ['conservative', 'balanced', 'aggressive'],
          description: 'System optimization strategy'
        }
      ]
    }
  ]

  const renderSetting = (setting: any) => {
    const value = config[setting.key as keyof typeof config]

    switch (setting.type) {
      case 'slider':
        return (
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-light">{setting.label}</span>
              <span className="text-sm font-medium text-white">{value}</span>
            </div>
            <input
              type="range"
              min={setting.min}
              max={setting.max}
              step={setting.step}
              value={value as number}
              onChange={(e) => handleConfigChange(setting.key, parseFloat(e.target.value))}
              className="w-full h-2 bg-background-secondary rounded-lg appearance-none cursor-pointer slider"
            />
            <p className="text-xs text-gray-medium">{setting.description}</p>
          </div>
        )

      case 'number':
        return (
          <div className="space-y-2">
            <label className="text-sm text-gray-light">{setting.label}</label>
            <input
              type="number"
              min={setting.min}
              max={setting.max}
              value={value as number}
              onChange={(e) => handleConfigChange(setting.key, parseInt(e.target.value))}
              className="w-full input-field"
            />
            <p className="text-xs text-gray-medium">{setting.description}</p>
          </div>
        )

      case 'toggle':
        return (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-light">{setting.label}</span>
              <button
                onClick={() => handleConfigChange(setting.key, !value)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  value ? 'bg-purple-primary' : 'bg-background-secondary'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    value ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
            <p className="text-xs text-gray-medium">{setting.description}</p>
          </div>
        )

      case 'select':
        return (
          <div className="space-y-2">
            <label className="text-sm text-gray-light">{setting.label}</label>
            <select
              value={value as string}
              onChange={(e) => handleConfigChange(setting.key, e.target.value)}
              className="w-full input-field"
            >
              {setting.options.map((option: string) => (
                <option key={option} value={option} className="bg-background-secondary">
                  {option.charAt(0).toUpperCase() + option.slice(1)}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-medium">{setting.description}</p>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="glass-panel p-6"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Sliders className="w-6 h-6 text-purple-primary" />
            <h2 className="text-2xl font-bold text-white">System Configuration</h2>
          </div>
          
          <div className="flex items-center space-x-2">
            {hasChanges && (
              <div className="flex items-center space-x-2 text-yellow-400 text-sm">
                <AlertCircle className="w-4 h-4" />
                <span>Unsaved changes</span>
              </div>
            )}
            
            {saveStatus === 'saved' && (
              <div className="flex items-center space-x-2 text-green-400 text-sm">
                <CheckCircle className="w-4 h-4" />
                <span>Saved successfully</span>
              </div>
            )}
            
            <button
              onClick={handleReset}
              className="btn-secondary flex items-center space-x-2"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Reset</span>
            </button>
            
            <button
              onClick={handleSave}
              disabled={!hasChanges || saveStatus === 'saving'}
              className="btn-primary flex items-center space-x-2 disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              <span>{saveStatus === 'saving' ? 'Saving...' : 'Save Changes'}</span>
            </button>
          </div>
        </div>
      </motion.div>

      {/* Configuration Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {configSections.map((section, sectionIndex) => {
          const Icon = section.icon
          
          return (
            <motion.div
              key={section.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: sectionIndex * 0.1 }}
              className="glass-panel p-6"
            >
              <div className="flex items-center space-x-3 mb-6">
                <Icon className={`w-5 h-5 ${section.color}`} />
                <h3 className="text-xl font-semibold text-white">{section.title}</h3>
              </div>

              <div className="space-y-6">
                {section.settings.map((setting, settingIndex) => (
                  <motion.div
                    key={setting.key}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: settingIndex * 0.05 }}
                  >
                    {renderSetting(setting)}
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
