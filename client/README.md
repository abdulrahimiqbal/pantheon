# Pantheon Frontend Dashboard

A modern, dynamic React/Next.js dashboard for the Pantheon AI physics research platform.

## Features

- **Dark Mode UI**: Deep purple accents with smooth animations
- **Dashboard Overview**: Real-time metrics and system status
- **Research Panel**: AI-powered research assistant with hypothesis generation
- **Visualization Panel**: Interactive charts and data visualization
- **Configuration Panel**: System and model parameter configuration
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Smooth animations and transitions
- **Recharts**: Data visualization library
- **Lucide React**: Modern icon library

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
client/
├── app/                 # Next.js app directory
│   ├── globals.css     # Global styles
│   ├── layout.tsx      # Root layout
│   └── page.tsx        # Main page
├── components/         # React components
│   ├── Dashboard.tsx   # Main dashboard
│   ├── Sidebar.tsx     # Navigation sidebar
│   ├── Header.tsx      # Top header
│   ├── ResearchPanel.tsx    # Research interface
│   ├── VisualizationPanel.tsx # Data visualization
│   ├── ConfigPanel.tsx      # Configuration settings
│   ├── MetricCard.tsx       # Metric display cards
│   ├── ActivityTimeline.tsx # Activity feed
│   └── SystemMetrics.tsx    # System health metrics
└── public/             # Static assets
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

## Design System

### Colors
- **Background**: Deep dark tones (#0a0a0f, #1a1a2e, #16213e)
- **Purple Accents**: Primary (#6366f1), Secondary (#8b5cf6), Accent (#a855f7)
- **Status Colors**: Green (success), Yellow (warning), Red (error)

### Components
- **Glass Panels**: Semi-transparent backgrounds with blur effects
- **Gradient Borders**: Subtle purple gradients for emphasis
- **Smooth Animations**: Framer Motion for fluid interactions
- **Responsive Layout**: Mobile-first design approach

## Future Enhancements

- Backend API integration
- Real-time WebSocket connections
- User authentication
- Advanced data visualization
- Export functionality
- Theme customization
