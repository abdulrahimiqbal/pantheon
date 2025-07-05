'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  BarChart3, 
  LineChart, 
  PieChart, 
  TrendingUp,
  Download,
  Settings,
  Maximize2
} from 'lucide-react'
import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart as RechartsBarChart,
  Bar,
  PieChart as RechartsPieChart,
  Cell,
  Pie
} from 'recharts'

export default function VisualizationPanel() {
  const [activeChart, setActiveChart] = useState('line')

  // Sample data for different chart types
  const lineData = [
    { name: 'Jan', experiments: 12, hypotheses: 8, validations: 5 },
    { name: 'Feb', experiments: 19, hypotheses: 12, validations: 8 },
    { name: 'Mar', experiments: 15, hypotheses: 18, validations: 12 },
    { name: 'Apr', experiments: 25, hypotheses: 22, validations: 15 },
    { name: 'May', experiments: 22, hypotheses: 28, validations: 18 },
    { name: 'Jun', experiments: 30, hypotheses: 25, validations: 22 },
  ]

  const barData = [
    { name: 'Quantum Physics', value: 45, color: '#6366f1' },
    { name: 'Astrophysics', value: 38, color: '#8b5cf6' },
    { name: 'Particle Physics', value: 32, color: '#a855f7' },
    { name: 'Cosmology', value: 28, color: '#c084fc' },
    { name: 'Theoretical Physics', value: 25, color: '#d8b4fe' },
  ]

  const pieData = [
    { name: 'Completed', value: 45, color: '#10b981' },
    { name: 'In Progress', value: 30, color: '#f59e0b' },
    { name: 'Pending', value: 15, color: '#ef4444' },
    { name: 'Archived', value: 10, color: '#6b7280' },
  ]

  const chartTypes = [
    { id: 'line', label: 'Timeline', icon: LineChart },
    { id: 'bar', label: 'Research Areas', icon: BarChart3 },
    { id: 'pie', label: 'Status Distribution', icon: PieChart },
  ]

  const renderChart = () => {
    switch (activeChart) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <RechartsLineChart data={lineData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1a1a2e', 
                  border: '1px solid #6366f1',
                  borderRadius: '8px'
                }} 
              />
              <Line 
                type="monotone" 
                dataKey="experiments" 
                stroke="#6366f1" 
                strokeWidth={2}
                dot={{ fill: '#6366f1', strokeWidth: 2 }}
              />
              <Line 
                type="monotone" 
                dataKey="hypotheses" 
                stroke="#8b5cf6" 
                strokeWidth={2}
                dot={{ fill: '#8b5cf6', strokeWidth: 2 }}
              />
              <Line 
                type="monotone" 
                dataKey="validations" 
                stroke="#a855f7" 
                strokeWidth={2}
                dot={{ fill: '#a855f7', strokeWidth: 2 }}
              />
            </RechartsLineChart>
          </ResponsiveContainer>
        )
      
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <RechartsBarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1a1a2e', 
                  border: '1px solid #6366f1',
                  borderRadius: '8px'
                }} 
              />
              <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </RechartsBarChart>
          </ResponsiveContainer>
        )
      
      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <RechartsPieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={120}
                paddingAngle={5}
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1a1a2e', 
                  border: '1px solid #6366f1',
                  borderRadius: '8px'
                }} 
              />
            </RechartsPieChart>
          </ResponsiveContainer>
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
            <TrendingUp className="w-6 h-6 text-purple-primary" />
            <h2 className="text-2xl font-bold text-white">Data Visualization</h2>
          </div>
          
          <div className="flex items-center space-x-2">
            <button className="btn-secondary flex items-center space-x-2">
              <Download className="w-4 h-4" />
              <span>Export</span>
            </button>
            <button className="btn-secondary">
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>
      </motion.div>

      {/* Chart Selection */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="glass-panel p-6"
      >
        <div className="flex items-center space-x-4 mb-6">
          {chartTypes.map((chart) => {
            const Icon = chart.icon
            return (
              <button
                key={chart.id}
                onClick={() => setActiveChart(chart.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                  activeChart === chart.id
                    ? 'bg-gradient-to-r from-purple-primary to-purple-secondary text-white'
                    : 'bg-background-tertiary text-gray-medium hover:text-white hover:bg-background-secondary'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{chart.label}</span>
              </button>
            )
          })}
        </div>

        <div className="bg-background-tertiary/30 rounded-lg p-4">
          {renderChart()}
        </div>
      </motion.div>

      {/* Data Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Experiments */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="glass-panel p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-white">Recent Experiments</h3>
            <button className="text-purple-primary hover:text-purple-secondary text-sm">
              View All
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-purple-primary/20">
                  <th className="text-left text-gray-medium py-2">Name</th>
                  <th className="text-left text-gray-medium py-2">Status</th>
                  <th className="text-left text-gray-medium py-2">Progress</th>
                </tr>
              </thead>
              <tbody className="space-y-2">
                {[
                  { name: 'Quantum Entanglement Study', status: 'Running', progress: 75 },
                  { name: 'Dark Matter Detection', status: 'Completed', progress: 100 },
                  { name: 'Higgs Boson Analysis', status: 'Pending', progress: 25 },
                  { name: 'Gravitational Waves', status: 'Running', progress: 60 },
                ].map((experiment, index) => (
                  <tr key={index} className="border-b border-gray-700/30">
                    <td className="py-3 text-gray-light">{experiment.name}</td>
                    <td className="py-3">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        experiment.status === 'Completed' 
                          ? 'bg-green-500/20 text-green-400'
                          : experiment.status === 'Running'
                          ? 'bg-blue-500/20 text-blue-400'
                          : 'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {experiment.status}
                      </span>
                    </td>
                    <td className="py-3">
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-background-secondary rounded-full h-2">
                          <div
                            className="h-2 bg-gradient-to-r from-purple-primary to-purple-accent rounded-full"
                            style={{ width: `${experiment.progress}%` }}
                          ></div>
                        </div>
                        <span className="text-xs text-gray-medium">{experiment.progress}%</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* Performance Metrics */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="glass-panel p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-white">Performance Metrics</h3>
            <button className="btn-secondary">
              <Maximize2 className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-4">
            {[
              { label: 'Hypothesis Accuracy', value: 87, color: 'bg-green-500' },
              { label: 'Processing Speed', value: 92, color: 'bg-blue-500' },
              { label: 'Data Quality', value: 78, color: 'bg-yellow-500' },
              { label: 'Model Confidence', value: 85, color: 'bg-purple-500' },
            ].map((metric, index) => (
              <div key={index} className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-light">{metric.label}</span>
                  <span className="text-sm font-medium text-white">{metric.value}%</span>
                </div>
                <div className="w-full bg-background-secondary rounded-full h-2">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${metric.value}%` }}
                    transition={{ duration: 1, delay: index * 0.2 }}
                    className={`h-2 rounded-full ${metric.color}`}
                  ></motion.div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
