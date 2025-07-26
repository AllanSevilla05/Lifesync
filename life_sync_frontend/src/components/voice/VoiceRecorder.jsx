import { useState, useEffect } from 'react';
import { Mic, MicOff, Volume2, VolumeX } from 'lucide-react';
import useSpeechRecognition from '../../hooks/useSpeechRecognition';
import './VoiceRecorder.css';

const VoiceRecorder = ({ onTranscriptChange, onRecordingComplete, placeholder = "Click microphone to start speaking..." }) => {
  const {
    isListening,
    transcript,
    error,
    isSupported,
    startListening,
    stopListening,
    resetTranscript,
    cleanup
  } = useSpeechRecognition();

  const [showVisualizer, setShowVisualizer] = useState(false);

  // Update parent component with transcript changes
  useEffect(() => {
    if (onTranscriptChange) {
      onTranscriptChange(transcript);
    }
  }, [transcript, onTranscriptChange]);

  // Handle recording completion
  useEffect(() => {
    if (!isListening && transcript && onRecordingComplete) {
      onRecordingComplete(transcript);
    }
  }, [isListening, transcript, onRecordingComplete]);

  // Cleanup on unmount
  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  const handleMicClick = () => {
    if (isListening) {
      stopListening();
      setShowVisualizer(false);
    } else {
      if (transcript) {
        resetTranscript();
      }
      startListening();
      setShowVisualizer(true);
    }
  };

  const handleClear = () => {
    resetTranscript();
    if (onTranscriptChange) {
      onTranscriptChange('');
    }
  };

  if (!isSupported) {
    return (
      <div className="voice-recorder unsupported">
        <div className="error-message">
          <VolumeX size={20} />
          <span>Speech recognition is not supported in this browser</span>
        </div>
      </div>
    );
  }

  return (
    <div className="voice-recorder">
      <div className="voice-controls">
        <button
          className={`mic-button ${isListening ? 'listening' : ''} ${error ? 'error' : ''}`}
          onClick={handleMicClick}
          disabled={!!error}
          aria-label={isListening ? 'Stop recording' : 'Start recording'}
        >
          {isListening ? <MicOff size={20} /> : <Mic size={20} />}
          {isListening && (
            <div className="pulse-ring"></div>
          )}
        </button>

        {transcript && (
          <button
            className="clear-button"
            onClick={handleClear}
            aria-label="Clear transcript"
          >
            Clear
          </button>
        )}
      </div>

      {/* Status indicator */}
      <div className="status-indicator">
        {isListening && (
          <div className="listening-indicator">
            <Volume2 size={16} />
            <span>Listening...</span>
            <div className="audio-visualizer">
              <div className="bar"></div>
              <div className="bar"></div>
              <div className="bar"></div>
              <div className="bar"></div>
            </div>
          </div>
        )}
        {error && (
          <div className="error-indicator">
            <VolumeX size={16} />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Transcript display */}
      <div className="transcript-display">
        {transcript ? (
          <div className="transcript-text">
            {transcript}
          </div>
        ) : (
          <div className="placeholder-text">
            {placeholder}
          </div>
        )}
      </div>

      {/* Voice tips */}
      {!transcript && !isListening && (
        <div className="voice-tips">
          <h4>Voice Tips:</h4>
          <ul>
            <li>Try: "Remind me to work out tomorrow at 6 PM"</li>
            <li>Try: "I have a meeting with John on Friday at 2 PM"</li>
            <li>Try: "Add grocery shopping to my list"</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default VoiceRecorder;