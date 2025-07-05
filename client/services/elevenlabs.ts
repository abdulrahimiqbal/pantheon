// ElevenLabs API Integration Service
// Add your API key to .env.local: NEXT_PUBLIC_ELEVENLABS_API_KEY=your_api_key_here

interface ElevenLabsVoice {
  voice_id: string
  name: string
  samples: any[]
  category: string
  fine_tuning: {
    is_allowed: boolean
    state: string
  }
  labels: Record<string, string>
  description: string
  preview_url: string
  available_for_tiers: string[]
  settings: {
    stability: number
    similarity_boost: number
    style: number
    use_speaker_boost: boolean
  }
}

interface TTSRequest {
  text: string
  voice_id: string
  model_id?: string
  voice_settings?: {
    stability: number
    similarity_boost: number
    style?: number
    use_speaker_boost?: boolean
  }
}

interface SpeakerVerificationRequest {
  audio_data: Blob
  voice_id?: string
}

class ElevenLabsService {
  private apiKey: string
  private baseUrl = 'https://api.elevenlabs.io/v1'

  constructor() {
    this.apiKey = process.env.NEXT_PUBLIC_ELEVENLABS_API_KEY || ''
    if (!this.apiKey) {
      console.warn('ElevenLabs API key not found. Add NEXT_PUBLIC_ELEVENLABS_API_KEY to your environment variables.')
    }
  }

  private getHeaders() {
    return {
      'Accept': 'audio/mpeg',
      'Content-Type': 'application/json',
      'xi-api-key': this.apiKey
    }
  }

  // Get available voices
  async getVoices(): Promise<ElevenLabsVoice[]> {
    if (!this.apiKey) {
      throw new Error('ElevenLabs API key not configured')
    }

    try {
      const response = await fetch(`${this.baseUrl}/voices`, {
        headers: {
          'xi-api-key': this.apiKey
        }
      })

      if (!response.ok) {
        throw new Error(`Failed to fetch voices: ${response.statusText}`)
      }

      const data = await response.json()
      return data.voices || []
    } catch (error) {
      console.error('Error fetching voices:', error)
      throw error
    }
  }

  // Text-to-Speech conversion
  async textToSpeech(request: TTSRequest): Promise<Blob> {
    if (!this.apiKey) {
      throw new Error('ElevenLabs API key not configured')
    }

    const url = `${this.baseUrl}/text-to-speech/${request.voice_id}`
    
    const payload = {
      text: request.text,
      model_id: request.model_id || 'eleven_monolingual_v1',
      voice_settings: {
        stability: request.voice_settings?.stability || 0.5,
        similarity_boost: request.voice_settings?.similarity_boost || 0.8,
        style: request.voice_settings?.style || 0,
        use_speaker_boost: request.voice_settings?.use_speaker_boost || true
      }
    }

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`TTS request failed: ${response.statusText} - ${errorText}`)
      }

      return await response.blob()
    } catch (error) {
      console.error('Error with text-to-speech:', error)
      throw error
    }
  }

  // Voice cloning - add voice sample
  async addVoice(name: string, audioFiles: File[], description?: string): Promise<string> {
    if (!this.apiKey) {
      throw new Error('ElevenLabs API key not configured')
    }

    const formData = new FormData()
    formData.append('name', name)
    
    if (description) {
      formData.append('description', description)
    }

    // Add audio files
    audioFiles.forEach((file, index) => {
      formData.append('files', file, `sample_${index}.wav`)
    })

    try {
      const response = await fetch(`${this.baseUrl}/voices/add`, {
        method: 'POST',
        headers: {
          'xi-api-key': this.apiKey
        },
        body: formData
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`Voice cloning failed: ${response.statusText} - ${errorText}`)
      }

      const data = await response.json()
      return data.voice_id
    } catch (error) {
      console.error('Error adding voice:', error)
      throw error
    }
  }

  // Voice cloning with audio recording
  async cloneVoice(audioBlob: Blob, voiceName: string, description?: string): Promise<string> {
    try {
      const formData = new FormData()
      
      // Convert blob to file
      const audioFile = new File([audioBlob], `${voiceName}.wav`, { type: 'audio/wav' })
      formData.append('files', audioFile)
      formData.append('name', voiceName)
      formData.append('description', description || `Cloned voice: ${voiceName}`)
      
      const response = await fetch(`${this.baseUrl}/voices/add`, {
        method: 'POST',
        headers: {
          'xi-api-key': this.apiKey,
        },
        body: formData
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(`Voice cloning failed: ${response.statusText} - ${errorData.detail || ''}`)
      }
      
      const result = await response.json()
      return result.voice_id
    } catch (error) {
      console.error('Voice cloning error:', error)
      throw error
    }
  }

  // Get cloned voices (user's custom voices)
  async getClonedVoices(): Promise<ElevenLabsVoice[]> {
    try {
      const voices = await this.getVoices()
      // Filter for cloned voices (category: 'cloned' or custom voices)
      return voices.filter(voice => 
        voice.category === 'cloned' || 
        voice.category === 'generated' ||
        !voice.category // Custom voices might not have category
      )
    } catch (error) {
      console.error('Error fetching cloned voices:', error)
      return []
    }
  }

  // Delete a cloned voice
  async deleteVoice(voiceId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/voices/${voiceId}`, {
        method: 'DELETE',
        headers: {
          'xi-api-key': this.apiKey,
        }
      })
      
      return response.ok
    } catch (error) {
      console.error('Error deleting voice:', error)
      return false
    }
  }

  // Speaker verification
  async verifySpeaker(audioBlob: Blob, referenceVoiceId?: string): Promise<boolean> {
    if (!this.apiKey) {
      console.warn('ElevenLabs API key not configured - skipping speaker verification')
      return true // Return true for demo purposes
    }

    // Note: This is a placeholder implementation
    // ElevenLabs doesn't have a direct speaker verification endpoint
    // You would need to implement this using voice similarity comparison
    // or integrate with a dedicated speaker verification service

    try {
      // Placeholder logic - in real implementation, you would:
      // 1. Convert audio to the required format
      // 2. Compare with reference voice samples
      // 3. Return similarity score above threshold

      console.log('Speaker verification would be implemented here')
      
      // Simulate verification delay
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // For demo, return true (verified)
      return true
    } catch (error) {
      console.error('Error with speaker verification:', error)
      return false
    }
  }

  // Get voice settings
  async getVoiceSettings(voiceId: string): Promise<any> {
    if (!this.apiKey) {
      throw new Error('ElevenLabs API key not configured')
    }

    try {
      const response = await fetch(`${this.baseUrl}/voices/${voiceId}/settings`, {
        headers: {
          'xi-api-key': this.apiKey
        }
      })

      if (!response.ok) {
        throw new Error(`Failed to get voice settings: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error getting voice settings:', error)
      throw error
    }
  }

  // Update voice settings
  async updateVoiceSettings(voiceId: string, settings: any): Promise<void> {
    if (!this.apiKey) {
      throw new Error('ElevenLabs API key not configured')
    }

    try {
      const response = await fetch(`${this.baseUrl}/voices/${voiceId}/settings/edit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'xi-api-key': this.apiKey
        },
        body: JSON.stringify(settings)
      })

      if (!response.ok) {
        throw new Error(`Failed to update voice settings: ${response.statusText}`)
      }
    } catch (error) {
      console.error('Error updating voice settings:', error)
      throw error
    }
  }

  // Stream text-to-speech (for real-time audio)
  async streamTextToSpeech(request: TTSRequest): Promise<ReadableStream> {
    if (!this.apiKey) {
      throw new Error('ElevenLabs API key not configured')
    }

    const url = `${this.baseUrl}/text-to-speech/${request.voice_id}/stream`
    
    const payload = {
      text: request.text,
      model_id: request.model_id || 'eleven_monolingual_v1',
      voice_settings: {
        stability: request.voice_settings?.stability || 0.5,
        similarity_boost: request.voice_settings?.similarity_boost || 0.8,
        style: request.voice_settings?.style || 0,
        use_speaker_boost: request.voice_settings?.use_speaker_boost || true
      }
    }

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        throw new Error(`Streaming TTS request failed: ${response.statusText}`)
      }

      if (!response.body) {
        throw new Error('No response body for streaming')
      }

      return response.body
    } catch (error) {
      console.error('Error with streaming text-to-speech:', error)
      throw error
    }
  }

  // Get user subscription info
  async getUserInfo(): Promise<any> {
    if (!this.apiKey) {
      throw new Error('ElevenLabs API key not configured')
    }

    try {
      const response = await fetch(`${this.baseUrl}/user`, {
        headers: {
          'xi-api-key': this.apiKey
        }
      })

      if (!response.ok) {
        throw new Error(`Failed to get user info: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error getting user info:', error)
      throw error
    }
  }
}

// Export singleton instance
export const elevenLabsService = new ElevenLabsService()

// Export types for use in components
export type { ElevenLabsVoice, TTSRequest, SpeakerVerificationRequest }
