'use client'

import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface Particle {
  id: number
  x: number
  y: number
  opacity: number
  scale: number
  delay: number
}

interface ClickSpark {
  id: number
  x: number
  y: number
  angle: number
  velocity: number
  life: number
}

export default function CursorEffect() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const [particles, setParticles] = useState<Particle[]>([])
  const [isVisible, setIsVisible] = useState(false)
  const [clickSparks, setClickSparks] = useState<ClickSpark[]>([])
  const [isClicking, setIsClicking] = useState(false)

  useEffect(() => {
    const updateMousePosition = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY })
      setIsVisible(true)
    }

    const handleMouseLeave = () => {
      setIsVisible(false)
    }

    const handleMouseEnter = () => {
      setIsVisible(true)
    }

    const handleMouseDown = (e: MouseEvent) => {
      setIsClicking(true)
      createClickSparks(e.clientX, e.clientY)
    }

    const handleMouseUp = () => {
      setIsClicking(false)
    }

    const createClickSparks = (x: number, y: number) => {
      const newSparks: ClickSpark[] = Array.from({ length: 16 }, (_, i) => ({
        id: Date.now() + i,
        x,
        y,
        angle: (i / 16) * Math.PI * 2 + (Math.random() - 0.5) * 0.5,
        velocity: 50 + Math.random() * 100,
        life: 1
      }))
      
      setClickSparks(prev => [...prev, ...newSparks])
      
      // Remove sparks after animation
      setTimeout(() => {
        setClickSparks(prev => prev.filter(spark => !newSparks.includes(spark)))
      }, 800)
    }

    // Create initial particles
    const initialParticles: Particle[] = Array.from({ length: 6 }, (_, i) => ({
      id: i,
      x: 0,
      y: 0,
      opacity: 0.7 + Math.random() * 0.3,
      scale: 0.3 + Math.random() * 0.4,
      delay: i * 0.08
    }))
    setParticles(initialParticles)

    window.addEventListener('mousemove', updateMousePosition)
    document.addEventListener('mouseleave', handleMouseLeave)
    document.addEventListener('mouseenter', handleMouseEnter)
    document.addEventListener('mousedown', handleMouseDown)
    document.addEventListener('mouseup', handleMouseUp)

    return () => {
      window.removeEventListener('mousemove', updateMousePosition)
      document.removeEventListener('mouseleave', handleMouseLeave)
      document.removeEventListener('mouseenter', handleMouseEnter)
      document.removeEventListener('mousedown', handleMouseDown)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [])

  return (
    <div className="fixed inset-0 pointer-events-none z-50">
      <AnimatePresence>
        {isVisible && (
          <>
            {/* Main cursor glow */}
            <motion.div
              className="absolute rounded-full bg-gradient-to-r from-orange-primary to-orange-accent cursor-glow"
              style={{
                width: isClicking ? 20 : 14,
                height: isClicking ? 20 : 14,
                left: mousePosition.x - (isClicking ? 10 : 7),
                top: mousePosition.y - (isClicking ? 10 : 7),
                filter: `blur(${isClicking ? 6 : 4}px)`,
              }}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ 
                scale: isClicking ? [1, 1.8, 1.3] : [1, 1.1, 1], 
                opacity: isClicking ? [0.7, 1, 0.8] : [0.6, 0.8, 0.6]
              }}
              exit={{ scale: 0, opacity: 0 }}
              transition={{ 
                duration: isClicking ? 0.3 : 0.8,
                ease: "easeOut",
                repeat: isClicking ? 0 : Infinity,
                repeatType: "reverse"
              }}
            />

            {/* Core cursor dot */}
            <motion.div
              className="absolute rounded-full bg-orange-primary cursor-core"
              style={{
                width: isClicking ? 8 : 4,
                height: isClicking ? 8 : 4,
                left: mousePosition.x - (isClicking ? 4 : 2),
                top: mousePosition.y - (isClicking ? 4 : 2),
              }}
              initial={{ scale: 0 }}
              animate={{ 
                scale: isClicking ? [1, 1.5, 1.2] : 1,
                rotate: isClicking ? [0, 180, 360] : 0
              }}
              exit={{ scale: 0 }}
              transition={{ 
                duration: isClicking ? 0.2 : 0.1, 
                ease: "easeOut"
              }}
            />

            {/* Orbiting particles */}
            {particles.map((particle, index) => {
              const angle = (index / particles.length) * Math.PI * 2
              const baseRadius = isClicking ? 35 : 25
              const radius = baseRadius + Math.sin(Date.now() * 0.003 + index) * 8
              const x = mousePosition.x + Math.cos(angle + Date.now() * 0.002) * radius
              const y = mousePosition.y + Math.sin(angle + Date.now() * 0.002) * radius
              const intensity = 0.6 + Math.sin(Date.now() * 0.004 + index) * 0.4

              return (
                <motion.div
                  key={particle.id}
                  className="absolute rounded-full bg-orange-accent"
                  style={{
                    width: isClicking ? 3 : 2,
                    height: isClicking ? 3 : 2,
                    left: x - (isClicking ? 1.5 : 1),
                    top: y - (isClicking ? 1.5 : 1),
                    boxShadow: `0 0 ${isClicking ? 8 : 4}px rgba(255, 107, 53, ${intensity})`,
                  }}
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ 
                    scale: isClicking ? particle.scale * 1.5 : particle.scale, 
                    opacity: intensity,
                  }}
                  exit={{ scale: 0, opacity: 0 }}
                  transition={{ 
                    duration: 0.2,
                    delay: particle.delay,
                    ease: "easeOut"
                  }}
                />
              )
            })}

            {/* Static charge lines */}
            {Array.from({ length: isClicking ? 12 : 8 }).map((_, i) => {
              const totalLines = isClicking ? 12 : 8
              const angle = (i / totalLines) * Math.PI * 2 + Date.now() * 0.005
              const baseLength = isClicking ? 25 : 15
              const length = baseLength + Math.sin(Date.now() * 0.01 + i) * (isClicking ? 15 : 8)
              const startRadius = isClicking ? 8 : 5
              const startX = mousePosition.x + Math.cos(angle) * startRadius
              const startY = mousePosition.y + Math.sin(angle) * startRadius
              const endX = startX + Math.cos(angle) * length
              const endY = startY + Math.sin(angle) * length
              const intensity = isClicking ? 0.9 : 0.6 + Math.sin(Date.now() * 0.012 + i) * 0.3

              return (
                <motion.div
                  key={`line-${i}`}
                  className="absolute charge-line"
                  style={{
                    left: startX,
                    top: startY,
                    width: Math.sqrt((endX - startX) ** 2 + (endY - startY) ** 2),
                    height: isClicking ? 2 : 1,
                    background: `linear-gradient(90deg, rgba(255, 107, 53, ${intensity}), rgba(255, 165, 0, ${intensity * 0.5}), rgba(255, 107, 53, 0))`,
                    transformOrigin: '0 50%',
                    transform: `rotate(${Math.atan2(endY - startY, endX - startX)}rad)`,
                    boxShadow: `0 0 ${isClicking ? 8 : 4}px rgba(255, 107, 53, ${intensity * 0.7})`,
                  }}
                  initial={{ scaleX: 0, opacity: 0 }}
                  animate={{ 
                    scaleX: isClicking ? [0, 1.5, 1] : [0, 1.2, 1], 
                    opacity: [0, intensity, intensity * (isClicking ? 0.8 : 0.6)]
                  }}
                  exit={{ scaleX: 0, opacity: 0 }}
                  transition={{ 
                    duration: isClicking ? 0.2 : 0.3,
                    delay: i * (isClicking ? 0.01 : 0.02),
                    ease: "easeOut"
                  }}
                />
              )
            })}

            {/* Click sparks */}
            {clickSparks.map((spark) => {
              const currentTime = Date.now()
              const age = (currentTime - spark.id) / 800 // 800ms lifespan
              const distance = spark.velocity * age
              const x = spark.x + Math.cos(spark.angle) * distance
              const y = spark.y + Math.sin(spark.angle) * distance
              const opacity = Math.max(0, 1 - age * 1.5)
              const scale = Math.max(0.2, 1 - age * 0.8)
              const brightness = Math.max(0.5, 2 - age * 1.5)

              return (
                <motion.div
                  key={spark.id}
                  className="absolute rounded-full"
                  style={{
                    left: x - 3,
                    top: y - 3,
                    width: 6,
                    height: 6,
                    background: `radial-gradient(circle, rgba(255, 165, 0, ${opacity}) 0%, rgba(255, 107, 53, ${opacity * 0.8}) 50%, rgba(255, 69, 0, ${opacity * 0.6}) 100%)`,
                    boxShadow: `0 0 ${12 * opacity}px rgba(255, 107, 53, ${opacity}), 0 0 ${6 * opacity}px rgba(255, 165, 0, ${opacity * 0.8})`,
                    filter: `brightness(${brightness}) blur(${(1 - opacity) * 2}px)`,
                  }}
                  initial={{ scale: 0, opacity: 1, rotate: 0 }}
                  animate={{ 
                    scale: [0.5, 1.5, scale],
                    opacity: [1, opacity * 1.2, opacity],
                    rotate: [0, 180, 360]
                  }}
                  exit={{ scale: 0, opacity: 0 }}
                  transition={{ 
                    duration: 0.8,
                    ease: [0.25, 0.46, 0.45, 0.94]
                  }}
                />
              )
            })}

            {/* Enhanced micro charges */}
            {Array.from({ length: isClicking ? 20 : 10 }).map((_, i) => {
              const totalCharges = isClicking ? 20 : 10
              const angle = (i / totalCharges) * Math.PI * 2 + Date.now() * 0.008
              const baseDistance = isClicking ? 45 : 35
              const distance = baseDistance + Math.sin(Date.now() * 0.006 + i) * (isClicking ? 15 : 8)
              const x = mousePosition.x + Math.cos(angle) * distance
              const y = mousePosition.y + Math.sin(angle) * distance
              const flickerIntensity = isClicking ? 0.8 : 0.4 + Math.sin(Date.now() * 0.025 + i) * 0.6

              return (
                <motion.div
                  key={`micro-${i}`}
                  className="absolute static-charge rounded-full"
                  style={{
                    left: x - (isClicking ? 1.5 : 1),
                    top: y - (isClicking ? 1.5 : 1),
                    width: isClicking ? 3 : 2,
                    height: isClicking ? 3 : 2,
                    background: `rgba(255, 107, 53, ${flickerIntensity})`,
                    boxShadow: `0 0 ${isClicking ? 10 : 6}px rgba(255, 107, 53, ${flickerIntensity})`,
                  }}
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ 
                    scale: isClicking ? [0.8, 1.2, 0.8] : [0.5, 1, 0.5],
                    opacity: [0, flickerIntensity, flickerIntensity * 0.3]
                  }}
                  exit={{ scale: 0, opacity: 0 }}
                  transition={{ 
                    duration: isClicking ? 0.3 : 0.5,
                    delay: i * (isClicking ? 0.01 : 0.02),
                    repeat: Infinity,
                    repeatType: "reverse",
                    ease: "easeInOut"
                  }}
                />
              )
            })}

            {/* Dynamic pulsing rings */}
            {Array.from({ length: isClicking ? 3 : 2 }).map((_, i) => {
              const size = (i + 1) * (isClicking ? 25 : 20)
              const delay = i * 0.2
              
              return (
                <motion.div
                  key={`ring-${i}`}
                  className="absolute border rounded-full"
                  style={{
                    left: mousePosition.x - size,
                    top: mousePosition.y - size,
                    width: size * 2,
                    height: size * 2,
                    borderColor: `rgba(255, 107, 53, ${isClicking ? 0.6 : 0.3})`,
                    borderWidth: isClicking ? 2 : 1,
                  }}
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ 
                    scale: isClicking ? [0.8, 1.3, 1] : [1, 1.2, 1],
                    opacity: isClicking ? [0.6, 0.2, 0.4] : [0.3, 0.1, 0.3]
                  }}
                  exit={{ scale: 0, opacity: 0 }}
                  transition={{ 
                    duration: isClicking ? 1.5 : 2,
                    delay,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                />
              )
            })}
          </>
        )}
      </AnimatePresence>
    </div>
  )
}
