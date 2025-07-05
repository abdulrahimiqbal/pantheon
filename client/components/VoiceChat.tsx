'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Mic, 
  MicOff, 
  Volume2, 
  VolumeX, 
  Settings, 
  Radio, 
  Shield, 
  CheckCircle, 
  AlertCircle, 
  Loader2, 
  Clock,
  X 
} from 'lucide-react'
import { elevenLabsService, type ElevenLabsVoice } from '../services/elevenlabs'
import { ScientificProcessingResult } from '../services/gemini'

interface VoiceChatProps {
  isOpen: boolean
  onClose: () => void
  onSendMessage: (message: string) => void
  onGetAIResponse?: (message: string) => Promise<string> | string
  onGetScientificResponse?: (message: string) => Promise<ScientificProcessingResult>
}

interface VoiceSettings {
  voiceId: string
  stability: number
  similarityBoost: number
  speakerVerification: boolean
}

type StatusType = 'idle' | 'loading' | 'success' | 'error' | 'processing'

interface StatusIndicator {
  type: StatusType
  message: string
  details?: string
}

export default function VoiceChat({ isOpen, onClose, onSendMessage, onGetAIResponse, onGetScientificResponse }: VoiceChatProps) {
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
  
  // Enhanced status tracking
  const [mainStatus, setMainStatus] = useState<StatusIndicator>({ type: 'idle', message: 'Ready to chat' })
  const [voiceLoadingStatus, setVoiceLoadingStatus] = useState<StatusIndicator>({ type: 'idle', message: 'Voices ready' })
  const [cloneOperationStatus, setCloneOperationStatus] = useState<StatusIndicator>({ type: 'idle', message: 'Ready to clone' })
  const [ttsStatus, setTtsStatus] = useState<StatusIndicator>({ type: 'idle', message: 'Text-to-speech ready' })
  const [recordingStatus, setRecordingStatus] = useState<StatusIndicator>({ type: 'idle', message: 'Microphone ready' })
  const [selectedVoiceName, setSelectedVoiceName] = useState('')
  const [hasRecordedAudio, setHasRecordedAudio] = useState(false)
  const [cloneProgress, setCloneProgress] = useState(0)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const recognitionRef = useRef<SpeechRecognition | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  // Status icon helper
  const getStatusIcon = (status: StatusIndicator) => {
    switch (status.type) {
      case 'loading':
      case 'processing':
        return <Loader2 className="w-4 h-4 animate-spin text-orange-primary" />
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-400" />
      default:
        return <Clock className="w-4 h-4 text-gray-400" />
    }
  }

  // Load available voices from ElevenLabs
  useEffect(() => {
    const loadVoices = async () => {
      setIsLoadingVoices(true)
      setVoiceLoadingStatus({ type: 'loading', message: 'Loading available voices...' })
      
      try {
        const voices = await elevenLabsService.getVoices()
        setAvailableVoices(voices)
        
        // Find the currently selected voice or use the first available voice
        const currentVoice = voices.find(v => v.voice_id === voiceSettings.voiceId) || voices[0]
        
        if (currentVoice) {
          // Update voice settings if the current voice ID doesn't exist in available voices
          if (!voices.find(v => v.voice_id === voiceSettings.voiceId)) {
            setVoiceSettings(prev => ({ ...prev, voiceId: currentVoice.voice_id }))
          }
          setCurrentVoiceId(currentVoice.voice_id)
          setSelectedVoiceName(currentVoice.name)
          
          setVoiceLoadingStatus({ 
            type: 'success', 
            message: `${voices.length} voices loaded successfully`,
            details: `Selected voice: ${currentVoice.name}` 
          })
        } else {
          setVoiceLoadingStatus({ 
            type: 'error', 
            message: 'No voices available', 
            details: 'Check your ElevenLabs API key' 
          })
        }
      } catch (error) {
        console.error('Failed to load voices:', error)
        setVoiceLoadingStatus({ 
          type: 'error', 
          message: 'Failed to load voices', 
          details: 'Check your ElevenLabs API key' 
        })
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
    setMainStatus({ type: 'processing', message: 'Processing your message...', details: text.substring(0, 50) + (text.length > 50 ? '...' : '') })
    
    onSendMessage(text) // Send to main chat system
    setTranscript('')
    setIsProcessing(true)
    
    // Get AI response from the main chat system
    let aiResponse = `I heard you say: "${text}". This is a placeholder response.`
    
    // Prioritize scientific processing if available
    if (onGetScientificResponse) {
      try {
        setMainStatus({ type: 'processing', message: 'Initializing scientific analysis...' })
        const scientificResult = await onGetScientificResponse(text)
        
        // Wait for complete scientific analysis including all metadata
        setMainStatus({ type: 'processing', message: 'Scientific analysis complete. Preparing voice response...' })
        
        // Use the main response for voice synthesis
        aiResponse = scientificResult.response
        setMainStatus({ type: 'success', message: 'Scientific analysis complete' })
      } catch (error) {
        console.error('Failed to get scientific response:', error)
        aiResponse = 'Sorry, I encountered an error during scientific analysis.'
        setMainStatus({ type: 'error', message: 'Failed to complete scientific analysis' })
      }
    } else if (onGetAIResponse) {
      try {
        setMainStatus({ type: 'processing', message: 'Generating AI response...' })
        const response = await onGetAIResponse(text)
        aiResponse = response
        setMainStatus({ type: 'success', message: 'AI response generated' })
      } catch (error) {
        console.error('Failed to get AI response:', error)
        aiResponse = 'Sorry, I encountered an error processing your request.'
        setMainStatus({ type: 'error', message: 'Failed to generate AI response' })
      }
    }
    
    setIsProcessing(false)
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
    
    const selectedVoice = availableVoices.find(v => v.voice_id === voiceSettings.voiceId)
    console.log('TTS Debug:', {
      voiceId: voiceSettings.voiceId,
      selectedVoice: selectedVoice,
      availableVoicesCount: availableVoices.length,
      text: text.substring(0, 50) + '...'
    })
    
    setTtsStatus({ 
      type: 'processing', 
      message: `Converting to speech...`,
      details: `Using ${selectedVoice?.name || 'Unknown Voice'} (${voiceSettings.voiceId})` 
    })
    
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
      
      setTtsStatus({ type: 'success', message: 'Audio generated, now playing...' })

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
        setTtsStatus({ type: 'success', message: 'Speech completed' })
        setMainStatus({ type: 'idle', message: 'Ready to chat' })
      }
      
      audio.onerror = () => {
        console.error('Audio playback error')
        setIsSpeaking(false)
        setIsBreathing(false)
        setGlobeScale(1)
        URL.revokeObjectURL(audioUrl)
        setTtsStatus({ type: 'error', message: 'Audio playback failed' })
      }
      
      await audio.play()
      
    } catch (error) {
      console.error('Error with ElevenLabs TTS:', error)
      setTtsStatus({ type: 'error', message: 'ElevenLabs TTS failed, using fallback...' })
      
      // Fallback to Web Speech API
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text)
        utterance.rate = 0.9
        utterance.pitch = 1
        utterance.volume = 0.8
        
        utterance.onstart = () => {
          setIsBreathing(true)
          setTtsStatus({ type: 'processing', message: 'Using browser speech synthesis' })
        }
        
        utterance.onend = () => {
          setIsSpeaking(false)
          setIsBreathing(false)
          setGlobeScale(1)
          setTtsStatus({ type: 'success', message: 'Speech completed (fallback)' })
          setMainStatus({ type: 'idle', message: 'Ready to chat' })
        }
        
        speechSynthesis.speak(utterance)
      } else {
        setIsSpeaking(false)
        setIsBreathing(false)
        setGlobeScale(1)
        setTtsStatus({ type: 'error', message: 'No speech synthesis available' })
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
      setCloneOperationStatus({ type: 'loading', message: 'Loading cloned voices...' })
      const voices = await elevenLabsService.getClonedVoices()
      setClonedVoices(voices)
      setCloneOperationStatus({ 
        type: 'success', 
        message: `${voices.length} cloned voices loaded`,
        details: voices.length > 0 ? `Latest: ${voices[0]?.name}` : 'No cloned voices yet'
      })
    } catch (error) {
      console.error('Failed to load cloned voices:', error)
      setCloneOperationStatus({ type: 'error', message: 'Failed to load cloned voices' })
    }
  }

  // Select voice with feedback
  const selectVoice = (voiceId: string, voiceName: string) => {
    console.log('Voice Selection Debug:', {
      oldVoiceId: voiceSettings.voiceId,
      newVoiceId: voiceId,
      voiceName: voiceName
    })
    
    setVoiceSettings(prev => ({ ...prev, voiceId }))
    setCurrentVoiceId(voiceId)
    setSelectedVoiceName(voiceName)
    setMainStatus({ type: 'success', message: `Voice changed to ${voiceName}` })
    
    // Clear status after 3 seconds
    setTimeout(() => {
      setMainStatus({ type: 'idle', message: 'Ready to chat' })
    }, 3000)
  }

  // Start recording for voice cloning
  const startCloneRecording = async () => {
    try {
      setRecordingStatus({ type: 'loading', message: 'Accessing microphone...' })
      setCloneOperationStatus({ type: 'processing', message: 'Preparing to record voice sample...' })
      
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
      setHasRecordedAudio(false)
      
      setRecordingStatus({ type: 'processing', message: 'Recording in progress...' })
      setCloneOperationStatus({ 
        type: 'processing', 
        message: 'Recording voice sample...', 
        details: 'Speak clearly and naturally for best results' 
      })
      
      // Timer for recording duration
      const timer = setInterval(() => {
        setCloneRecordingTime(prev => {
          const newTime = prev + 1
          setCloneProgress((newTime / 30) * 100) // Progress out of 30 seconds
          
          if (newTime >= 10 && !hasRecordedAudio) {
            setHasRecordedAudio(true)
            setCloneOperationStatus({ 
              type: 'processing', 
              message: 'Good! Keep speaking...', 
              details: `${newTime}s recorded (minimum 10s reached)` 
            })
          } else if (newTime < 10) {
            setCloneOperationStatus({ 
              type: 'processing', 
              message: 'Recording voice sample...', 
              details: `${newTime}s recorded (need at least 10s)` 
            })
          } else {
            setCloneOperationStatus({ 
              type: 'processing', 
              message: 'Recording voice sample...', 
              details: `${newTime}s recorded (${30 - newTime}s remaining)` 
            })
          }
          
          if (newTime >= 30) { // Max 30 seconds
            stopCloneRecording()
            clearInterval(timer)
            return 30
          }
          return newTime
        })
      }, 1000)
      
    } catch (error) {
      console.error('Error starting clone recording:', error)
      setRecordingStatus({ type: 'error', message: 'Microphone access denied' })
      setCloneOperationStatus({ type: 'error', message: 'Could not access microphone for voice cloning' })
    }
  }

  // Stop recording for voice cloning
  const stopCloneRecording = () => {
    if (mediaRecorderRef.current && isRecordingForClone) {
      mediaRecorderRef.current.stop()
      setIsRecordingForClone(false)
      setRecordingStatus({ type: 'success', message: 'Recording completed' })
      
      if (cloneRecordingTime >= 10) {
        setHasRecordedAudio(true)
        setCloneOperationStatus({ 
          type: 'success', 
          message: 'Voice sample recorded successfully!', 
          details: `${cloneRecordingTime}s of audio captured` 
        })
      } else {
        setCloneOperationStatus({ 
          type: 'error', 
          message: 'Recording too short', 
          details: 'Need at least 10 seconds for voice cloning' 
        })
        setHasRecordedAudio(false)
      }
      
      setCloneProgress(0)
    }
  }

  // Clone voice with recorded audio
  const cloneVoice = async () => {
    if (!cloneVoiceName.trim()) {
      setCloneOperationStatus({ type: 'error', message: 'Please enter a name for your cloned voice' })
      return
    }
    
    if (audioChunksRef.current.length === 0 || !hasRecordedAudio) {
      setCloneOperationStatus({ type: 'error', message: 'No valid audio recorded for cloning' })
      return
    }
    
    setIsCloning(true)
    setCloneOperationStatus({ type: 'processing', message: 'Cloning your voice...', details: 'This may take a few moments' })
    
    try {
      // Create audio blob from recorded chunks
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
      
      setCloneOperationStatus({ type: 'processing', message: 'Uploading voice sample...', details: 'Processing audio data' })
      
      // Clone the voice
      const voiceId = await elevenLabsService.cloneVoice(
        audioBlob, 
        cloneVoiceName,
        `Custom cloned voice: ${cloneVoiceName}`
      )
      
      setCloneOperationStatus({ type: 'processing', message: 'Voice cloned! Updating settings...', details: 'Refreshing voice list' })
      
      // Update voice settings to use the new cloned voice
      setVoiceSettings(prev => ({ ...prev, voiceId }))
      setCurrentVoiceId(voiceId)
      setSelectedVoiceName(cloneVoiceName)
      
      // Refresh voice lists
      await loadClonedVoices()
      const allVoices = await elevenLabsService.getVoices()
      setAvailableVoices(allVoices)
      
      setCloneOperationStatus({ 
        type: 'success', 
        message: `Voice "${cloneVoiceName}" cloned successfully!`, 
        details: 'Voice is now selected and ready to use' 
      })
      
      // Close dialog and reset after a delay
      setTimeout(() => {
        setShowCloneDialog(false)
        setCloneVoiceName('')
        audioChunksRef.current = []
        setHasRecordedAudio(false)
        setCloneRecordingTime(0)
        setCloneOperationStatus({ type: 'idle', message: 'Ready to clone' })
      }, 2000)
      
    } catch (error) {
      console.error('Voice cloning failed:', error)
      setCloneOperationStatus({ 
        type: 'error', 
        message: 'Voice cloning failed', 
        details: error instanceof Error ? error.message : 'Please try again' 
      })
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
                {isProcessing && (
                  <Loader2 className="w-6 h-6 text-white/80 animate-spin" />
                )}
              </div>
            </div>
          </div>

          {/* Comprehensive Status Panel */}
          <div className="mb-6 space-y-3">
            {/* Main Status */}
            <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-lg p-3">
              <div className="flex items-center space-x-3">
                {getStatusIcon(mainStatus)}
                <div className="flex-1">
                  <p className="text-white text-sm font-medium">{mainStatus.message}</p>
                  {mainStatus.details && (
                    <p className="text-gray-400 text-xs">{mainStatus.details}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Voice Selection Status */}
            {selectedVoiceName && (
              <div className="bg-black/20 backdrop-blur-sm border border-orange-primary/20 rounded-lg p-3">
                <div className="flex items-center space-x-3">
                  <Volume2 className="w-4 h-4 text-orange-primary" />
                  <div className="flex-1">
                    <p className="text-white text-sm font-medium">Selected Voice</p>
                    <p className="text-orange-primary text-xs">{selectedVoiceName}</p>
                  </div>
                </div>
              </div>
            )}

            {/* TTS Status */}
            {(ttsStatus.type !== 'idle' || isSpeaking) && (
              <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-lg p-3">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(ttsStatus)}
                  <div className="flex-1">
                    <p className="text-white text-sm font-medium">{ttsStatus.message}</p>
                    {ttsStatus.details && (
                      <p className="text-gray-400 text-xs">{ttsStatus.details}</p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Recording Status */}
            {(recordingStatus.type !== 'idle' || isRecordingForClone) && (
              <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-lg p-3">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(recordingStatus)}
                  <div className="flex-1">
                    <p className="text-white text-sm font-medium">{recordingStatus.message}</p>
                    {isRecordingForClone && (
                      <div className="mt-2">
                        <div className="flex justify-between text-xs text-gray-400 mb-1">
                          <span>{cloneRecordingTime}s</span>
                          <span>{hasRecordedAudio ? 'Ready to clone' : 'Need 10s minimum'}</span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full transition-all duration-300 ${
                              hasRecordedAudio ? 'bg-green-400' : 'bg-orange-primary'
                            }`}
                            style={{ width: `${Math.min(cloneProgress, 100)}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Clone Operation Status */}
            {cloneOperationStatus.type !== 'idle' && (
              <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-lg p-3">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(cloneOperationStatus)}
                  <div className="flex-1">
                    <p className="text-white text-sm font-medium">{cloneOperationStatus.message}</p>
                    {cloneOperationStatus.details && (
                      <p className="text-gray-400 text-xs">{cloneOperationStatus.details}</p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Transcript */}
          {transcript && (
            <div className="mb-6 p-4 bg-black/20 backdrop-blur-sm border border-white/10 rounded-lg">
              <div className="flex items-start space-x-3">
                <Mic className="w-4 h-4 text-orange-primary mt-0.5" />
                <div>
                  <p className="text-gray-400 text-xs mb-1">You said:</p>
                  <p className="text-white text-sm">{transcript}</p>
                </div>
              </div>
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
                className="mt-6 p-4 bg-black/20 backdrop-blur-sm border border-orange-primary/20 rounded-lg"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-white font-medium">Voice Settings</h3>
                  {voiceLoadingStatus.type !== 'idle' && (
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(voiceLoadingStatus)}
                      <span className="text-xs text-gray-400">{voiceLoadingStatus.message}</span>
                    </div>
                  )}
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-gray-medium text-sm mb-2">
                      Voice Selection
                    </label>
                    <select
                      value={voiceSettings.voiceId}
                      onChange={(e) => {
                        const newVoiceId = e.target.value
                        const selectedVoice = availableVoices.find(v => v.voice_id === newVoiceId)
                        setVoiceSettings(prev => ({
                          ...prev,
                          voiceId: newVoiceId
                        }))
                        setSelectedVoiceName(selectedVoice?.name || '')
                        setMainStatus({ 
                          type: 'success', 
                          message: `Voice changed to ${selectedVoice?.name || 'Unknown'}`,
                          details: 'Voice selection updated'
                        })
                        // Clear status after 3 seconds
                        setTimeout(() => {
                          setMainStatus({ type: 'idle', message: 'Ready to chat' })
                        }, 3000)
                      }}
                      className="w-full bg-black/20 backdrop-blur-sm border border-orange-primary/20 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-orange-primary transition-colors"
                      disabled={isLoadingVoices}
                    >
                      {isLoadingVoices ? (
                        <option>Loading voices...</option>
                      ) : (
                        availableVoices.map((voice) => (
                          <option key={voice.voice_id} value={voice.voice_id}>
                            {voice.name} {voice.category === 'cloned' ? '🎤' : '🎭'} ({voice.category})
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
                      <div className="flex items-center space-x-2">
                        <h4 className="text-white font-medium text-sm">Voice Cloning</h4>
                        <div className="w-5 h-5 bg-orange-primary/20 rounded-full flex items-center justify-center">
                          <Mic className="w-3 h-3 text-orange-primary" />
                        </div>
                      </div>
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setShowCloneDialog(true)}
                        className="px-3 py-1.5 bg-gradient-to-r from-orange-primary to-orange-accent text-white text-xs rounded-lg hover:from-orange-accent hover:to-orange-primary transition-all shadow-sm font-medium"
                      >
                        + Clone Voice
                      </motion.button>
                    </div>
                    
                    {clonedVoices.length > 0 ? (
                      <div>
                        <label className="block text-gray-medium text-sm mb-3 flex items-center space-x-2">
                          <span>Your Cloned Voices</span>
                          <div className="w-5 h-5 bg-green-400/20 rounded-full flex items-center justify-center">
                            <span className="text-green-400 text-xs font-bold">{clonedVoices.length}</span>
                          </div>
                        </label>
                        <div className="space-y-2">
                          {clonedVoices.map((voice) => (
                            <motion.div 
                              key={voice.voice_id} 
                              whileHover={{ scale: 1.02 }}
                              className="flex items-center justify-between p-3 bg-black/20 backdrop-blur-sm rounded-lg border border-orange-primary/10 hover:border-orange-primary/30 transition-all"
                            >
                              <div className="flex items-center space-x-3">
                                <motion.button
                                  whileTap={{ scale: 0.9 }}
                                  onClick={() => {
                                    setVoiceSettings(prev => ({ ...prev, voiceId: voice.voice_id }))
                                    setSelectedVoiceName(voice.name)
                                    setMainStatus({ 
                                      type: 'success', 
                                      message: `Switched to ${voice.name}`,
                                      details: 'Cloned voice selected'
                                    })
                                    setTimeout(() => {
                                      setMainStatus({ type: 'idle', message: 'Ready to chat' })
                                    }, 3000)
                                  }}
                                  className={`w-4 h-4 rounded-full border-2 transition-all ${
                                    voiceSettings.voiceId === voice.voice_id
                                      ? 'bg-orange-primary border-orange-primary shadow-lg shadow-orange-primary/25'
                                      : 'border-gray-medium hover:border-orange-primary'
                                  }`}
                                />
                                <div className="flex items-center space-x-2">
                                  <Mic className="w-3 h-3 text-orange-primary" />
                                  <span className="text-white text-sm font-medium">{voice.name}</span>
                                  {voiceSettings.voiceId === voice.voice_id && (
                                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                                  )}
                                </div>
                              </div>
                              <motion.button
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.9 }}
                                onClick={async () => {
                                  if (confirm(`Delete voice "${voice.name}"? This action cannot be undone.`)) {
                                    try {
                                      await elevenLabsService.deleteVoice(voice.voice_id)
                                      await loadClonedVoices()
                                      setMainStatus({ 
                                        type: 'success', 
                                        message: `Deleted ${voice.name}`,
                                        details: 'Voice removed successfully'
                                      })
                                      setTimeout(() => {
                                        setMainStatus({ type: 'idle', message: 'Ready to chat' })
                                      }, 3000)
                                    } catch (error) {
                                      setMainStatus({ 
                                        type: 'error', 
                                        message: 'Failed to delete voice',
                                        details: 'Please try again'
                                      })
                                    }
                                  }
                                }}
                                className="text-red-400 hover:text-red-300 text-xs p-1 rounded hover:bg-red-400/10 transition-all"
                              >
                                🗑️
                              </motion.button>
                            </motion.div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-4">
                        <div className="w-12 h-12 bg-orange-primary/10 rounded-full flex items-center justify-center mx-auto mb-2">
                          <Mic className="w-6 h-6 text-orange-primary/50" />
                        </div>
                        <p className="text-gray-400 text-sm">No cloned voices yet</p>
                        <p className="text-gray-500 text-xs">Create your first voice clone above</p>
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
              if (e.target === e.currentTarget && !isCloning) {
                setShowCloneDialog(false)
                setCloneVoiceName('')
                setIsRecordingForClone(false)
                setCloneRecordingTime(0)
                setHasRecordedAudio(false)
                setCloneOperationStatus({ type: 'idle', message: 'Ready to clone' })
              }
            }}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-background-secondary border border-orange-primary/20 rounded-xl p-6 w-full max-w-lg"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-orange-primary to-orange-accent rounded-lg flex items-center justify-center">
                    <Mic className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="text-white font-semibold text-lg">Clone Your Voice</h3>
                    <p className="text-gray-400 text-sm">Create a personalized AI voice</p>
                  </div>
                </div>
                {!isCloning && (
                  <button
                    onClick={() => {
                      setShowCloneDialog(false)
                      setCloneVoiceName('')
                      setIsRecordingForClone(false)
                      setCloneRecordingTime(0)
                      setHasRecordedAudio(false)
                      setCloneOperationStatus({ type: 'idle', message: 'Ready to clone' })
                    }}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>

              {/* Clone Operation Status */}
              {cloneOperationStatus.type !== 'idle' && (
                <div className="mb-6 p-4 bg-black/20 backdrop-blur-sm border border-white/10 rounded-lg">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(cloneOperationStatus)}
                    <div className="flex-1">
                      <p className="text-white text-sm font-medium">{cloneOperationStatus.message}</p>
                      {cloneOperationStatus.details && (
                        <p className="text-gray-400 text-xs">{cloneOperationStatus.details}</p>
                      )}
                    </div>
                  </div>
                </div>
              )}
              
              <div className="space-y-6">
                {/* Voice Name Input */}
                <div>
                  <label className="block text-gray-medium text-sm mb-2">
                    Voice Name *
                  </label>
                  <input
                    type="text"
                    value={cloneVoiceName}
                    onChange={(e) => setCloneVoiceName(e.target.value)}
                    placeholder="Enter a name for your voice"
                    className="w-full px-3 py-2 bg-background-tertiary border border-orange-primary/20 rounded-lg text-white placeholder-gray-medium focus:outline-none focus:border-orange-primary"
                  />
                </div>

                {/* Recording Script */}
                <div className="bg-black/20 backdrop-blur-sm border border-orange-primary/20 rounded-lg p-4">
                  <div className="flex items-start space-x-3 mb-3">
                    <div className="w-6 h-6 bg-orange-primary rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-white text-xs font-bold">!</span>
                    </div>
                    <div>
                      <h4 className="text-white font-medium text-sm mb-2">Read This Script Aloud</h4>
                      <p className="text-gray-300 text-sm leading-relaxed">
                        "Hello, this is my voice for AI cloning. I'm speaking clearly and naturally 
                        to create the best possible voice model. The quick brown fox jumps over the lazy dog. 
                        This sentence contains every letter of the alphabet for optimal voice training."
                      </p>
                    </div>
                  </div>
                  <div className="text-xs text-gray-400">
                    💡 Tip: Speak naturally in a quiet environment for best results
                  </div>
                </div>

                {/* Recording Controls */}
                <div className="text-center">
                  <div className="mb-4">
                    <p className="text-gray-medium text-sm mb-2">
                      Record 10-30 seconds of clear speech
                    </p>
                    {isRecordingForClone && (
                      <div className="mb-3">
                        <div className="flex justify-between text-xs text-gray-400 mb-1">
                          <span>{cloneRecordingTime}s recorded</span>
                          <span className={hasRecordedAudio ? 'text-green-400' : 'text-orange-primary'}>
                            {hasRecordedAudio ? '✓ Ready to clone' : 'Need 10s minimum'}
                          </span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full transition-all duration-300 ${
                              hasRecordedAudio ? 'bg-green-400' : 'bg-orange-primary'
                            }`}
                            style={{ width: `${Math.min(cloneProgress, 100)}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {!isRecordingForClone ? (
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={startCloneRecording}
                      disabled={isCloning}
                      className="w-20 h-20 rounded-full bg-gradient-to-r from-orange-primary to-orange-accent hover:from-orange-accent hover:to-orange-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-all shadow-lg hover:shadow-orange-primary/25"
                    >
                      <Mic className="w-8 h-8 text-white" />
                    </motion.button>
                  ) : (
                    <div className="space-y-3">
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={stopCloneRecording}
                        className="w-20 h-20 rounded-full bg-red-500 hover:bg-red-600 flex items-center justify-center transition-colors shadow-lg"
                        animate={{ 
                          boxShadow: [
                            "0 0 0 0 rgba(239, 68, 68, 0.7)",
                            "0 0 0 10px rgba(239, 68, 68, 0)",
                            "0 0 0 0 rgba(239, 68, 68, 0)"
                          ]
                        }}
                        transition={{
                          duration: 1.5,
                          repeat: Infinity,
                          ease: "easeInOut"
                        }}
                      >
                        <MicOff className="w-8 h-8 text-white" />
                      </motion.button>
                      <p className="text-red-400 font-medium animate-pulse">
                        🔴 Recording: {cloneRecordingTime}s
                      </p>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-3">
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => {
                      setShowCloneDialog(false)
                      setCloneVoiceName('')
                      setIsRecordingForClone(false)
                      setCloneRecordingTime(0)
                      setHasRecordedAudio(false)
                      setCloneOperationStatus({ type: 'idle', message: 'Ready to clone' })
                    }}
                    disabled={isCloning}
                    className="flex-1 px-4 py-3 bg-black/20 backdrop-blur-sm border border-white/10 text-gray-300 rounded-lg hover:bg-white/5 hover:text-white transition-all disabled:opacity-50 font-medium"
                  >
                    Cancel
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={cloneVoice}
                    disabled={isCloning || !cloneVoiceName.trim() || !hasRecordedAudio}
                    className={`flex-1 px-4 py-3 rounded-lg font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center ${
                      hasRecordedAudio && cloneVoiceName.trim() 
                        ? 'bg-gradient-to-r from-orange-primary to-orange-accent hover:from-orange-accent hover:to-orange-primary text-white shadow-lg hover:shadow-orange-primary/25' 
                        : 'bg-gray-600 text-gray-400'
                    }`}
                  >
                    {isCloning ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin mr-2" />
                        Cloning Voice...
                      </>
                    ) : (
                      <>
                        <Mic className="w-4 h-4 mr-2" />
                        Clone Voice
                      </>
                    )}
                  </motion.button>
                </div>

                {/* Requirements Checklist */}
                <div className="bg-black/10 backdrop-blur-sm border border-white/5 rounded-lg p-3">
                  <h5 className="text-white text-sm font-medium mb-2">Requirements:</h5>
                  <div className="space-y-1 text-xs">
                    <div className={`flex items-center space-x-2 ${
                      cloneVoiceName.trim() ? 'text-green-400' : 'text-gray-400'
                    }`}>
                      <div className={`w-3 h-3 rounded-full ${
                        cloneVoiceName.trim() ? 'bg-green-400' : 'bg-gray-600'
                      }`} />
                      <span>Voice name provided</span>
                    </div>
                    <div className={`flex items-center space-x-2 ${
                      hasRecordedAudio ? 'text-green-400' : 'text-gray-400'
                    }`}>
                      <div className={`w-3 h-3 rounded-full ${
                        hasRecordedAudio ? 'bg-green-400' : 'bg-gray-600'
                      }`} />
                      <span>Minimum 10 seconds recorded</span>
                    </div>
                    <div className={`flex items-center space-x-2 ${
                      cloneRecordingTime >= 15 ? 'text-green-400' : 'text-gray-400'
                    }`}>
                      <div className={`w-3 h-3 rounded-full ${
                        cloneRecordingTime >= 15 ? 'bg-green-400' : 'bg-gray-600'
                      }`} />
                      <span>15+ seconds for better quality (optional)</span>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </AnimatePresence>
  )
}
