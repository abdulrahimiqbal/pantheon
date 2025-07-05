'use client'

import { motion } from 'framer-motion'
import { 
  Brain, 
  Zap, 
  Database, 
  TrendingUp, 
  Clock,
  CheckCircle,
  AlertCircle,
  Activity
} from 'lucide-react'
import MetricCard from './MetricCard'
import ActivityTimeline from './ActivityTimeline'
import SystemMetrics from './SystemMetrics'

export default function Dashboard() {
  const metrics = [
    {
      title: 'Active Agents',
      value: '12',
      change: '+2',
      icon: Brain,
      color: 'text-purple-primary'
    },
    {
      title: 'Experiments Running',
      value: '8',
      change: '+3',
      icon: Zap,
      color: 'text-blue-400'
    },
    {
      title: 'Data Points',
      value: '2.4M',
      change: '+12%',
      icon: Database,
      color: 'text-green-400'
    },
    {
      title: 'Hypotheses Generated',
      value: '156',
      change: '+8',
      icon: TrendingUp,
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
      icon: CheckCircle,
      color: 'text-green-400'
    },
    {
      id: 2,
      type: 'hypothesis',
      title: 'Dark Matter Interaction Model',
      status: 'in-progress',
      timestamp: '5 minutes ago',
      icon: Clock,
      color: 'text-yellow-400'
    },
    {
      id: 3,
      type: 'alert',
      title: 'Anomaly Detected in Dataset #47',
      status: 'attention',
      timestamp: '12 minutes ago',
      icon: AlertCircle,
      color: 'text-red-400'
    },
    {
      id: 4,
      type: 'agent',
      title: 'New Agent Deployed: Particle Physics Specialist',
      status: 'active',
      timestamp: '1 hour ago',
      icon: Brain,
      color: 'text-purple-primary'
    }
  ]

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
            <MetricCard {...metric} />
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
              <Activity className="w-5 h-5 text-purple-primary" />
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
