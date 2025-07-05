# Voice Chat Integration with ElevenLabs

This document explains the voice chat functionality integrated into the Pantheon AI frontend, including ElevenLabs API integration for high-quality text-to-speech and voice verification.

## Features

### 🎤 Voice Input
- **Speech Recognition**: Uses Web Speech API for real-time voice-to-text conversion
- **Audio Level Monitoring**: Visual feedback showing microphone input levels
- **Continuous Listening**: Supports ongoing conversation with automatic speech detection
- **Multi-language Support**: Configurable language settings (default: English US)

### 🔊 Voice Output
- **ElevenLabs TTS**: High-quality text-to-speech using ElevenLabs API
- **Voice Selection**: Choose from available ElevenLabs voices
- **Voice Settings**: Adjustable stability and similarity boost parameters
- **Fallback Support**: Web Speech API fallback when ElevenLabs is unavailable

### 🛡️ Security Features
- **Speaker Verification**: Voice identity verification (placeholder implementation)
- **Voice Enrollment**: Ability to enroll user's voice for verification
- **Secure API Key Handling**: Environment variable configuration for API keys

## Setup Instructions

### 1. ElevenLabs API Configuration

1. **Get API Key**:
   - Visit [ElevenLabs Dashboard](https://elevenlabs.io/app/settings/api-keys)
   - Create an account and generate an API key

2. **Configure Environment Variables**:
   ```bash
   # Copy the example file
   cp .env.example .env.local
   
   # Add your API key to .env.local
   NEXT_PUBLIC_ELEVENLABS_API_KEY=your_api_key_here
   ```

3. **Optional Voice ID Configuration**:
   ```bash
   # Set a default voice ID (optional)
   NEXT_PUBLIC_DEFAULT_VOICE_ID=pNInz6obpgDQGcFmaJgB
   ```

### 2. Browser Permissions

The voice chat requires microphone access. Users will be prompted to allow microphone permissions when first using the feature.

### 3. HTTPS Requirement

Voice chat features require HTTPS in production due to browser security policies for microphone access.

## Usage

### Accessing Voice Chat

1. **From Research Panel**: Click the microphone button in the chat input area
2. **Voice Chat Modal**: The voice chat interface opens as an overlay
3. **Start Conversation**: Click "Start Listening" to begin voice interaction

### Voice Chat Controls

- **🎤 Start/Stop Listening**: Toggle voice input
- **🔊 Mute/Unmute**: Control voice output
- **⚙️ Settings**: Adjust voice parameters and preferences
- **🛡️ Voice Verification**: Enable/disable speaker verification
- **📝 Enrollment**: Enroll your voice for verification

### Voice Settings

- **Voice Selection**: Choose from available ElevenLabs voices
- **Stability** (0.0-1.0): Controls voice consistency
- **Similarity Boost** (0.0-1.0): Enhances voice similarity to original
- **Speaker Verification**: Toggle identity verification

## Technical Implementation

### Components

1. **VoiceChat.tsx**: Main voice chat component
2. **elevenlabs.ts**: ElevenLabs API service integration
3. **speech.d.ts**: TypeScript definitions for Web Speech API

### API Integration

```typescript
// Text-to-Speech Example
const audioBlob = await elevenLabsService.textToSpeech({
  text: "Hello, how can I help you?",
  voice_id: "pNInz6obpgDQGcFmaJgB",
  voice_settings: {
    stability: 0.5,
    similarity_boost: 0.8,
    use_speaker_boost: true
  }
})
```

### Voice Verification

```typescript
// Speaker Verification (Placeholder)
const isVerified = await elevenLabsService.verifySpeaker(
  audioBlob, 
  referenceVoiceId
)
```

## Troubleshooting

### Common Issues

1. **No Microphone Access**:
   - Check browser permissions
   - Ensure HTTPS connection
   - Try refreshing the page

2. **ElevenLabs API Errors**:
   - Verify API key is correct
   - Check API quota/limits
   - Ensure network connectivity

3. **Voice Not Playing**:
   - Check browser audio settings
   - Verify speakers/headphones
   - Try different voice settings

### Error Handling

The system includes comprehensive error handling:
- Graceful fallback to Web Speech API
- User-friendly error messages
- Automatic retry mechanisms
- Console logging for debugging

## Browser Compatibility

### Supported Browsers
- ✅ Chrome 25+
- ✅ Firefox 44+
- ✅ Safari 14.1+
- ✅ Edge 79+

### Required Features
- Web Speech API (Speech Recognition)
- Web Audio API (Audio processing)
- MediaDevices API (Microphone access)
- Fetch API (ElevenLabs integration)

## Security Considerations

### API Key Security
- Never commit API keys to version control
- Use environment variables for configuration
- Consider server-side proxy for production

### Voice Data Privacy
- Audio data is processed locally when possible
- ElevenLabs API calls are made directly from client
- No voice data is stored permanently

### Speaker Verification
- Current implementation is placeholder
- Production systems should use dedicated verification services
- Consider biometric security standards

## Performance Optimization

### Audio Processing
- Efficient audio buffer management
- Real-time audio level monitoring
- Optimized speech recognition settings

### API Usage
- Voice caching for repeated phrases
- Streaming TTS for long content
- Rate limiting and quota management

## Future Enhancements

### Planned Features
- [ ] Real speaker verification implementation
- [ ] Voice cloning capabilities
- [ ] Multi-language voice support
- [ ] Voice emotion detection
- [ ] Background noise cancellation
- [ ] Voice command shortcuts

### Integration Possibilities
- [ ] Backend voice processing
- [ ] Voice analytics and insights
- [ ] Custom voice model training
- [ ] Real-time voice translation
- [ ] Voice-controlled UI navigation

## Support

For issues or questions:
1. Check browser console for error messages
2. Verify API key configuration
3. Test with different browsers
4. Review ElevenLabs API documentation
5. Contact development team for assistance

## API Documentation

- [ElevenLabs API Docs](https://docs.elevenlabs.io/)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
