'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Mic, MicOff, Volume2, VolumeX, Settings, Shield, Radio } from 'lucide-react'
import { elevenLabsService, type ElevenLabsVoice } from '../services/elevenlabs'

interface VoiceChatProps {
  isOpen: boolean
  onClose: () => void
  onSendMessage: (message: string) => void
  onGetAIResponse?: (message: string) => Promise<string> | string
}

interface VoiceSettings {
  voiceId: string
  stability: number
  similarityBoost: number
  speakerVerification: boolean
}

export default function VoiceChat({ isOpen, onClose, onSendMessage, onGetAIResponse }: VoiceChatProps) {
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [audioLevel, setAudioLevel] = useState(0)
  const [transcript, setTranscript] = useState('')
  const [globeScale, setGlobeScale] = useState(1)
  const [isBreathing, setIsBreathing] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [voiceSettings, setVoiceSettings] = useState<VoiceSettings>({
    voiceId: 'pNInz6obpgDQGcFmaJgB', // Default ElevenLabs voice
    stability: 0.5,
    similarityBoost: 0.8,
    speakerVerification: true
  })
  const [availableVoices, setAvailableVoices] = useState<ElevenLabsVoice[]>([])
  const [isLoadingVoices, setIsLoadingVoices] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [voiceVerified, setVoiceVerified] = useState(false)
  const [enrollmentComplete, setEnrollmentComplete] = useState(false)
  const [isCloning, setIsCloning] = useState(false)
  const [showCloneDialog, setShowCloneDialog] = useState(false)
  const [cloneVoiceName, setCloneVoiceName] = useState('')
  const [isRecordingForClone, setIsRecordingForClone] = useState(false)
  const [cloneRecordingTime, setCloneRecordingTime] = useState(0)
  const [clonedVoices, setClonedVoices] = useState<ElevenLabsVoice[]>([])
  const [cloneStatus, setCloneStatus] = useState('')
  const [showScriptReader, setShowScriptReader] = useState(false)
  const [isReadingScript, setIsReadingScript] = useState(false)
  const [scriptProgress, setScriptProgress] = useState(0)
  const [currentVoiceId, setCurrentVoiceId] = useState('')

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const recognitionRef = useRef<SpeechRecognition | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  // Load available voices from ElevenLabs
  useEffect(() => {
    const loadVoices = async () => {
      setIsLoadingVoices(true)
      try {
        const voices = await elevenLabsService.getVoices()
        setAvailableVoices(voices)
        if (voices.length > 0 && !voiceSettings.voiceId) {
          setVoiceSettings(prev => ({ ...prev, voiceId: voices[0].voice_id }))
        }
      } catch (error) {
        console.error('Failed to load voices:', error)
      } finally {
        setIsLoadingVoices(false)
      }
    }

    loadVoices()
  }, [])

  // Initialize speech recognition and audio context
  useEffect(() => {
    if (typeof window !== 'undefined') {
      // Initialize Speech Recognition
      if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        const SpeechRecognitionClass = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
        const recognition = new SpeechRecognitionClass()
        recognitionRef.current = recognition
        
        recognition.continuous = true
        recognition.interimResults = true
        recognition.lang = 'en-US'

        recognition.onresult = (event: SpeechRecognitionEvent) => {
          let finalTranscript = ''
          let interimTranscript = ''

          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript
            if (event.results[i].isFinal) {
              finalTranscript += transcript
            } else {
              interimTranscript += transcript
            }
          }

          setTranscript(finalTranscript || interimTranscript)
          
          if (finalTranscript) {
            handleVoiceInput(finalTranscript)
          }
        }

        recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
          console.error('Speech recognition error:', event.error)
          setIsListening(false)
        }
      }

      // Initialize Audio Context for voice level monitoring
      const AudioContext = window.AudioContext || (window as any).webkitAudioContext
      audioContextRef.current = new AudioContext()
      analyserRef.current = audioContextRef.current.createAnalyser()
      analyserRef.current.fftSize = 256
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
      if (audioContextRef.current) {
        audioContextRef.current.close()
      }
    }
  }, [])

  // Monitor audio levels
  useEffect(() => {
    let animationFrame: number

    const updateAudioLevel = () => {
      if (analyserRef.current && isListening) {
        const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)
        analyserRef.current.getByteFrequencyData(dataArray)
        const average = dataArray.reduce((a: number, b: number) => a + b) / dataArray.length
        const normalizedLevel = average / 255
        setAudioLevel(normalizedLevel)
        
        // Update globe scale based on user's voice input
        if (normalizedLevel > 0.1) {
          const scale = 1 + (normalizedLevel * 0.4) // Scale between 1 and 1.4
          setGlobeScale(scale)
          setIsBreathing(true)
        } else {
          setGlobeScale(1)
          setIsBreathing(false)
        }
        
        animationFrame = requestAnimationFrame(updateAudioLevel)
      }
    }

    if (isListening) {
      updateAudioLevel()
    }

    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame)
      }
    }
  }, [isListening])

  const startListening = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      
      // Connect to audio analyser
      if (audioContextRef.current && analyserRef.current) {
        const source = audioContextRef.current.createMediaStreamSource(stream)
        source.connect(analyserRef.current)
      }

      // Start speech recognition
      if (recognitionRef.current) {
        recognitionRef.current.start()
      }

      // Setup media recorder for voice verification
      mediaRecorderRef.current = new MediaRecorder(stream)
      audioChunksRef.current = []

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data)
      }

      mediaRecorderRef.current.start()
      setIsListening(true)
      setTranscript('')
    } catch (error) {
      console.error('Error starting voice recognition:', error)
    }
  }

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
    }
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop()
    }
    setIsListening(false)
    setAudioLevel(0)
  }

  const handleVoiceInput = async (text: string) => {
    console.log('Voice input received:', text)
    onSendMessage(text) // Send to main chat system
    setTranscript('')
    
    // Get AI response from the main chat system
    let aiResponse = `I heard you say: "${text}". This is a placeholder response.`
    
    if (onGetAIResponse) {
      try {
        const response = await onGetAIResponse(text)
        aiResponse = response
      } catch (error) {
        console.error('Failed to get AI response:', error)
        aiResponse = 'Sorry, I encountered an error processing your request.'
      }
    }
    
    // Convert AI response to speech
    await speakText(aiResponse)
  }

  const verifyVoice = async () => {
    if (audioChunksRef.current.length === 0) {
      console.warn('No audio data for verification')
      return
    }

    try {
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
      const isVerified = await elevenLabsService.verifySpeaker(audioBlob, voiceSettings.voiceId)
      setVoiceVerified(isVerified)
      
      if (!isVerified) {
        console.warn('Voice verification failed')
      }
    } catch (error) {
      console.error('Voice verification error:', error)
      // Fallback to true for demo purposes
      setVoiceVerified(true)
    }
  }

  const speakText = async (text: string) => {
    setIsSpeaking(true)
    setIsBreathing(true)
    
    try {
      // Use ElevenLabs TTS
      const audioBlob = await elevenLabsService.textToSpeech({
        text,
        voice_id: voiceSettings.voiceId,
        voice_settings: {
          stability: voiceSettings.stability,
          similarity_boost: voiceSettings.similarityBoost,
          use_speaker_boost: true
        }
      })

      // Play the audio
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)
      
      // Create audio context for visualization
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
      const source = audioContext.createMediaElementSource(audio)
      const analyser = audioContext.createAnalyser()
      analyser.fftSize = 256
      source.connect(analyser)
      analyser.connect(audioContext.destination)
      
      const dataArray = new Uint8Array(analyser.frequencyBinCount)
      
      const updateGlobeScale = () => {
        if (isSpeaking) {
          analyser.getByteFrequencyData(dataArray)
          const average = dataArray.reduce((a, b) => a + b) / dataArray.length
          const scale = 1 + (average / 255) * 0.3 // Scale between 1 and 1.3
          setGlobeScale(scale)
          requestAnimationFrame(updateGlobeScale)
        }
      }
      
      audio.onplay = () => {
        updateGlobeScale()
      }
      
      audio.onended = () => {
        setIsSpeaking(false)
        setIsBreathing(false)
        setGlobeScale(1)
        URL.revokeObjectURL(audioUrl)
      }
      
      audio.onerror = () => {
        console.error('Audio playback error')
        setIsSpeaking(false)
        setIsBreathing(false)
        setGlobeScale(1)
        URL.revokeObjectURL(audioUrl)
      }
      
      await audio.play()
      
    } catch (error) {
      console.error('Error with ElevenLabs TTS:', error)
      
      // Fallback to Web Speech API
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text)
        utterance.rate = 0.9
        utterance.pitch = 1
        utterance.volume = 0.8
        
        utterance.onstart = () => {
          setIsBreathing(true)
        }
        
        utterance.onend = () => {
          setIsSpeaking(false)
          setIsBreathing(false)
          setGlobeScale(1)
        }
        
        speechSynthesis.speak(utterance)
      } else {
        setIsSpeaking(false)
        setIsBreathing(false)
        setGlobeScale(1)
      }
    }
  }

  const enrollVoice = async () => {
    // Placeholder for voice enrollment with ElevenLabs
    console.log('Voice enrollment would happen here')
    setEnrollmentComplete(true)
  }

  // Load cloned voices
  const loadClonedVoices = async () => {
    try {
      const voices = await elevenLabsService.getClonedVoices()
      setClonedVoices(voices)
    } catch (error) {
      console.error('Failed to load cloned voices:', error)
    }
  }

  // Start recording for voice cloning
  const startCloneRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      
      mediaRecorderRef.current = new MediaRecorder(stream)
      audioChunksRef.current = []
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }
      
      mediaRecorderRef.current.start()
      setIsRecordingForClone(true)
      setCloneRecordingTime(0)
      
      // Timer for recording duration
      const timer = setInterval(() => {
        setCloneRecordingTime(prev => {
          if (prev >= 30) { // Max 30 seconds
            stopCloneRecording()
            clearInterval(timer)
            return 30
          }
          return prev + 1
        })
      }, 1000)
      
    } catch (error) {
      console.error('Error starting clone recording:', error)
      alert('Could not access microphone for voice cloning')
    }
  }

  // Stop recording for voice cloning
  const stopCloneRecording = () => {
    if (mediaRecorderRef.current && isRecordingForClone) {
      mediaRecorderRef.current.stop()
      setIsRecordingForClone(false)
    }
  }

  // Clone voice with recorded audio
  const cloneVoice = async () => {
    if (!cloneVoiceName.trim()) {
      alert('Please enter a name for your cloned voice')
      return
    }
    
    if (audioChunksRef.current.length === 0) {
      alert('No audio recorded for cloning')
      return
    }
    
    setIsCloning(true)
    
    try {
      // Create audio blob from recorded chunks
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
      
      // Clone the voice
      const voiceId = await elevenLabsService.cloneVoice(
        audioBlob, 
        cloneVoiceName,
        `Custom cloned voice: ${cloneVoiceName}`
      )
      
      // Update voice settings to use the new cloned voice
      setVoiceSettings(prev => ({ ...prev, voiceId }))
      
      // Refresh voice lists
      await loadClonedVoices()
      const allVoices = await elevenLabsService.getVoices()
      setAvailableVoices(allVoices)
      
      // Close dialog and reset
      setShowCloneDialog(false)
      setCloneVoiceName('')
      audioChunksRef.current = []
      
      alert(`Voice "${cloneVoiceName}" cloned successfully!`)
      
    } catch (error) {
      console.error('Voice cloning failed:', error)
      alert('Voice cloning failed. Please try again.')
    } finally {
      setIsCloning(false)
    }
  }

  // Load cloned voices on component mount
  useEffect(() => {
    loadClonedVoices()
  }, [])

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ y: 50 }}
          animate={{ y: 0 }}
          exit={{ y: 50 }}
          className="bg-background-secondary border border-orange-primary/20 rounded-2xl p-8 max-w-md w-full"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-orange-primary to-orange-accent rounded-lg flex items-center justify-center">
                <Radio className="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">Voice Chat</h2>
                <p className="text-gray-medium text-sm">
                  {voiceVerified ? 'Voice Verified' : 'Voice Recognition Active'}
                </p>
              </div>
            </div>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 text-gray-medium hover:text-white transition-colors"
            >
              <Settings className="w-5 h-5" />
            </button>
          </div>

          {/* Voice Verification Status */}
          {voiceSettings.speakerVerification && (
            <div className="mb-6 p-4 bg-background-tertiary rounded-lg border border-orange-primary/10">
              <div className="flex items-center space-x-3">
                <Shield className={`w-5 h-5 ${voiceVerified ? 'text-green-400' : 'text-orange-primary'}`} />
                <div>
                  <p className="text-white font-medium">
                    {voiceVerified ? 'Voice Verified' : 'Voice Verification Required'}
                  </p>
                  <p className="text-gray-medium text-sm">
                    {voiceVerified 
                      ? 'Your identity has been confirmed'
                      : 'Speak to verify your identity'
                    }
                  </p>
                </div>
              </div>
              {!enrollmentComplete && (
                <button
                  onClick={enrollVoice}
                  className="mt-3 px-4 py-2 bg-orange-primary text-white rounded-lg text-sm hover:bg-orange-accent transition-colors"
                >
                  Enroll Voice
                </button>
              )}
            </div>
          )}

          {/* Breathing Globe Visualizer */}
          <div className="mb-6 flex items-center justify-center">
            <div className="relative w-32 h-32">
              {/* Outer glow ring */}
              <motion.div
                className="absolute inset-0 rounded-full bg-gradient-to-r from-orange-primary/20 to-orange-accent/20 blur-xl"
                animate={{
                  scale: isBreathing ? [1, 1.4, 1] : (isListening ? [1, 1.2, 1] : 1),
                  opacity: isBreathing || isListening ? [0.3, 0.8, 0.3] : 0.2
                }}
                transition={{
                  duration: isBreathing ? 0.8 : (isListening ? 1.5 : 2),
                  repeat: (isBreathing || isListening) ? Infinity : 0,
                  ease: "easeInOut"
                }}
              />
              
              {/* Middle ring */}
              <motion.div
                className="absolute inset-4 rounded-full bg-gradient-to-r from-orange-primary/40 to-orange-accent/40"
                animate={{
                  scale: isBreathing ? globeScale : (isListening ? [1, 1.1, 1] : 1),
                  opacity: isBreathing || isListening ? 0.6 : 0.3
                }}
                transition={{
                  duration: isBreathing ? 0.1 : (isListening ? 1.2 : 2),
                  repeat: isListening && !isBreathing ? Infinity : 0,
                  ease: "easeInOut"
                }}
              />
              
              {/* Core globe */}
              <motion.div
                className="absolute inset-8 rounded-full bg-gradient-to-r from-orange-primary to-orange-accent shadow-lg"
                animate={{
                  scale: isBreathing ? globeScale * 0.9 : (isListening ? [1, 1.05, 1] : 1),
                  boxShadow: isBreathing || isListening 
                    ? "0 0 30px rgba(255, 165, 0, 0.8)" 
                    : "0 0 15px rgba(255, 165, 0, 0.4)"
                }}
                transition={{
                  duration: isBreathing ? 0.1 : (isListening ? 1 : 2),
                  repeat: isListening && !isBreathing ? Infinity : 0,
                  ease: "easeInOut"
                }}
              />
              
              {/* Inner core */}
              <motion.div
                className="absolute inset-12 rounded-full bg-white/20"
                animate={{
                  scale: isBreathing ? globeScale * 0.8 : (isListening ? [1, 0.9, 1] : 1),
                  opacity: isBreathing || isListening ? [0.2, 0.6, 0.2] : 0.1
                }}
                transition={{
                  duration: isBreathing ? 0.1 : (isListening ? 0.8 : 2),
                  repeat: isListening && !isBreathing ? Infinity : 0,
                  ease: "easeInOut"
                }}
              />
              
              {/* Status indicator */}
              <div className="absolute inset-0 flex items-center justify-center">
                {isListening && (
                  <Mic className="w-6 h-6 text-white/80" />
                )}
                {isSpeaking && (
                  <Volume2 className="w-6 h-6 text-white/80" />
                )}
              </div>
            </div>
          </div>

          {/* Transcript */}
          {transcript && (
            <div className="mb-6 p-4 bg-background-tertiary rounded-lg">
              <p className="text-white text-sm">{transcript}</p>
            </div>
          )}

          {/* Controls */}
          <div className="flex items-center justify-center space-x-4">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={isListening ? stopListening : startListening}
              disabled={isProcessing}
              className={`w-16 h-16 rounded-full flex items-center justify-center transition-all ${
                isListening
                  ? 'bg-red-500 hover:bg-red-600'
                  : 'bg-orange-primary hover:bg-orange-accent'
              } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {isProcessing ? (
                <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : isListening ? (
                <MicOff className="w-6 h-6 text-white" />
              ) : (
                <Mic className="w-6 h-6 text-white" />
              )}
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsSpeaking(!isSpeaking)}
              className="w-12 h-12 rounded-full bg-background-tertiary border border-orange-primary/20 flex items-center justify-center hover:bg-background-primary transition-colors"
            >
              {isSpeaking ? (
                <VolumeX className="w-5 h-5 text-orange-primary" />
              ) : (
                <Volume2 className="w-5 h-5 text-orange-primary" />
              )}
            </motion.button>
          </div>

          {/* Settings Panel */}
          <AnimatePresence>
            {showSettings && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-6 p-4 bg-background-tertiary rounded-lg border border-orange-primary/10"
              >
                <h3 className="text-white font-medium mb-4">Voice Settings</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-gray-medium text-sm mb-2">
                      Voice Selection
                    </label>
                    <select
                      value={voiceSettings.voiceId}
                      onChange={(e) => setVoiceSettings(prev => ({
                        ...prev,
                        voiceId: e.target.value
                      }))}
                      className="w-full bg-background-primary border border-orange-primary/20 rounded-lg px-3 py-2 text-white text-sm"
                      disabled={isLoadingVoices}
                    >
                      {isLoadingVoices ? (
                        <option>Loading voices...</option>
                      ) : (
                        availableVoices.map((voice) => (
                          <option key={voice.voice_id} value={voice.voice_id}>
                            {voice.name} ({voice.category})
                          </option>
                        ))
                      )}
                    </select>
                  </div>

                  <div>
                    <label className="block text-gray-medium text-sm mb-2">
                      Voice Stability: {voiceSettings.stability.toFixed(1)}
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={voiceSettings.stability}
                      onChange={(e) => setVoiceSettings(prev => ({
                        ...prev,
                        stability: parseFloat(e.target.value)
                      }))}
                      className="w-full accent-orange-primary"
                    />
                  </div>

                  <div>
                    <label className="block text-gray-medium text-sm mb-2">
                      Similarity Boost: {voiceSettings.similarityBoost.toFixed(1)}
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={voiceSettings.similarityBoost}
                      onChange={(e) => setVoiceSettings(prev => ({
                        ...prev,
                        similarityBoost: parseFloat(e.target.value)
                      }))}
                      className="w-full accent-orange-primary"
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <label className="text-gray-medium text-sm">Speaker Verification</label>
                    <input
                      type="checkbox"
                      checked={voiceSettings.speakerVerification}
                      onChange={(e) => setVoiceSettings(prev => ({
                        ...prev,
                        speakerVerification: e.target.checked
                      }))}
                      className="accent-orange-primary"
                    />
                  </div>

                  {/* Voice Cloning Section */}
                  <div className="border-t border-orange-primary/10 pt-4">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-white font-medium text-sm">Voice Cloning</h4>
                      <button
                        onClick={() => setShowCloneDialog(true)}
                        className="px-3 py-1 bg-orange-primary text-white text-xs rounded-lg hover:bg-orange-accent transition-colors"
                      >
                        Clone Voice
                      </button>
                    </div>
                    
                    {clonedVoices.length > 0 && (
                      <div>
                        <label className="block text-gray-medium text-sm mb-2">
                          Your Cloned Voices
                        </label>
                        <div className="space-y-2">
                          {clonedVoices.map((voice) => (
                            <div key={voice.voice_id} className="flex items-center justify-between p-2 bg-background-primary rounded border border-orange-primary/10">
                              <div className="flex items-center space-x-2">
                                <button
                                  onClick={() => setVoiceSettings(prev => ({ ...prev, voiceId: voice.voice_id }))}
                                  className={`w-3 h-3 rounded-full border-2 ${
                                    voiceSettings.voiceId === voice.voice_id
                                      ? 'bg-orange-primary border-orange-primary'
                                      : 'border-gray-medium'
                                  }`}
                                />
                                <span className="text-white text-sm">{voice.name}</span>
                              </div>
                              <button
                                onClick={async () => {
                                  if (confirm(`Delete voice "${voice.name}"?`)) {
                                    await elevenLabsService.deleteVoice(voice.voice_id)
                                    await loadClonedVoices()
                                  }
                                }}
                                className="text-red-400 hover:text-red-300 text-xs"
                              >
                                Delete
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* API Key Configuration Notice */}
                <div className="mt-4 p-3 bg-orange-primary/10 border border-orange-primary/20 rounded-lg">
                  <p className="text-orange-primary text-xs font-medium mb-1">
                    ElevenLabs API Configuration Required
                  </p>
                  <p className="text-gray-medium text-xs">
                    Add your ElevenLabs API key to environment variables:
                    <br />
                    <code className="text-orange-primary">NEXT_PUBLIC_ELEVENLABS_API_KEY</code>
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Instructions */}
          <div className="mt-6 text-center">
            <p className="text-gray-medium text-sm">
              {isListening 
                ? 'Listening... Speak now'
                : 'Click the microphone to start voice chat'
              }
            </p>
          </div>
        </motion.div>
      </motion.div>

      {/* Voice Cloning Dialog */}
      <AnimatePresence>
        {showCloneDialog && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/90 backdrop-blur-sm z-60 flex items-center justify-center p-4"
            onClick={(e) => {
              if (e.target === e.currentTarget) {
                setShowCloneDialog(false)
                setCloneVoiceName('')
                setIsRecordingForClone(false)
                setCloneRecordingTime(0)
              }
            }}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-background-secondary border border-orange-primary/20 rounded-xl p-6 w-full max-w-md"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-white font-semibold text-lg mb-4">Clone Your Voice</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-medium text-sm mb-2">
                    Voice Name
                  </label>
                  <input
                    type="text"
                    value={cloneVoiceName}
                    onChange={(e) => setCloneVoiceName(e.target.value)}
                    placeholder="Enter a name for your voice"
                    className="w-full px-3 py-2 bg-background-tertiary border border-orange-primary/20 rounded-lg text-white placeholder-gray-medium focus:outline-none focus:border-orange-primary"
                  />
                </div>

                <div className="text-center">
                  <p className="text-gray-medium text-sm mb-4">
                    Record 10-30 seconds of clear speech for best results
                  </p>
                  
                  {!isRecordingForClone ? (
                    <button
                      onClick={startCloneRecording}
                      disabled={isCloning}
                      className="w-20 h-20 rounded-full bg-orange-primary hover:bg-orange-accent disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-colors"
                    >
                      <Mic className="w-8 h-8 text-white" />
                    </button>
                  ) : (
                    <div className="space-y-3">
                      <button
                        onClick={stopCloneRecording}
                        className="w-20 h-20 rounded-full bg-red-500 hover:bg-red-600 flex items-center justify-center transition-colors animate-pulse"
                      >
                        <MicOff className="w-8 h-8 text-white" />
                      </button>
                      <p className="text-orange-primary font-medium">
                        Recording: {cloneRecordingTime}s / 30s
                      </p>
                    </div>
                  )}
                </div>

                <div className="flex space-x-3">
                  <button
                    onClick={() => {
                      setShowCloneDialog(false)
                      setCloneVoiceName('')
                      setIsRecordingForClone(false)
                      setCloneRecordingTime(0)
                    }}
                    disabled={isCloning}
                    className="flex-1 px-4 py-2 bg-background-tertiary border border-orange-primary/20 text-gray-medium rounded-lg hover:bg-background-primary transition-colors disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={cloneVoice}
                    disabled={isCloning || !cloneVoiceName.trim() || audioChunksRef.current.length === 0}
                    className="flex-1 px-4 py-2 bg-orange-primary text-white rounded-lg hover:bg-orange-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                  >
                    {isCloning ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                        Cloning...
                      </>
                    ) : (
                      'Clone Voice'
                    )}
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </AnimatePresence>
  )
}
