const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3001;

// Security middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
}));

// CORS middleware
app.use(cors({
  origin: process.env.NODE_ENV === 'production' 
    ? ['https://your-domain.com'] 
    : ['http://localhost:3000'],
  credentials: true
}));

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Static file serving
app.use('/static', express.static(path.join(__dirname, 'public')));

// API routes placeholder
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    service: 'pantheon-server'
  });
});

// Placeholder API endpoints for future backend integration
app.get('/api/agents', (req, res) => {
  res.json({
    agents: [
      { id: 1, name: 'Physics Specialist', status: 'active', type: 'specialist' },
      { id: 2, name: 'Data Analyst', status: 'active', type: 'generalist' },
      { id: 3, name: 'Hypothesis Generator', status: 'idle', type: 'specialist' }
    ]
  });
});

app.get('/api/experiments', (req, res) => {
  res.json({
    experiments: [
      { id: 1, name: 'Quantum Entanglement Study', status: 'running', progress: 75 },
      { id: 2, name: 'Dark Matter Detection', status: 'completed', progress: 100 },
      { id: 3, name: 'Higgs Boson Analysis', status: 'pending', progress: 25 }
    ]
  });
});

app.get('/api/metrics', (req, res) => {
  res.json({
    system: {
      cpu: Math.floor(Math.random() * 30) + 60,
      memory: Math.floor(Math.random() * 20) + 40,
      network: Math.floor(Math.random() * 25) + 70,
      power: Math.floor(Math.random() * 10) + 85
    },
    research: {
      activeAgents: 12,
      experimentsRunning: 8,
      dataPoints: '2.4M',
      hypothesesGenerated: 156
    }
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ 
    error: 'Something went wrong!',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Internal server error'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

app.listen(PORT, () => {
  console.log(`🚀 Pantheon server running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/api/health`);
  console.log(`🔬 Environment: ${process.env.NODE_ENV || 'development'}`);
});
