import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Loader } from 'lucide-react';
import { apiService } from '../../services/api';
import './VoiceInput.css';

const VoiceInput = ({ onTasksCreated, onError }) => {
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState('');
    const [conversationHistory, setConversationHistory] = useState([]);
    const [currentSession, setCurrentSession] = useState('');
    
    const recognitionRef = useRef(null);

    useEffect(() => {
        // Check if browser supports speech recognition
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            setError('Speech recognition is not supported in this browser');
            return;
        }

        // Initialize speech recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognitionRef.current = new SpeechRecognition();
        
        const recognition = recognitionRef.current;
        recognition.continuous = true; // Keep listening continuously
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        recognition.maxAlternatives = 1;

        // Set longer timeout for silence detection
        recognition.silenceTimeout = 10000; // 10 seconds of silence before stopping
        recognition.noSpeechTimeout = 15000; // 15 seconds of no speech before stopping

        recognition.onstart = () => {
            setIsListening(true);
            setError('');
            setTranscript('');
            // Start a new session
            setCurrentSession('');
        };

        recognition.onresult = (event) => {
            let finalTranscript = '';
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            const fullTranscript = finalTranscript + interimTranscript;
            setTranscript(fullTranscript);
            setCurrentSession(fullTranscript);
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            setIsListening(false);
            
            switch (event.error) {
                case 'no-speech':
                    setError('No speech detected. Please try again.');
                    break;
                case 'audio-capture':
                    setError('Audio capture failed. Please check your microphone.');
                    break;
                case 'not-allowed':
                    setError('Microphone access denied. Please allow microphone access.');
                    break;
                case 'network':
                    setError('Network error. Please check your connection.');
                    break;
                case 'service-not-allowed':
                    setError('Speech recognition service not allowed.');
                    break;
                default:
                    setError('Speech recognition failed. Please try again.');
            }
        };

        recognition.onend = () => {
            setIsListening(false);
            // If we have a transcript and we're not processing, keep the transcript visible
            if (transcript && !isProcessing) {
                // Don't clear the transcript automatically
            }
        };

        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.stop();
            }
        };
    }, []);

    const startListening = () => {
        if (recognitionRef.current) {
            try {
                recognitionRef.current.start();
            } catch (error) {
                console.error('Error starting speech recognition:', error);
                setError('Failed to start voice recognition');
            }
        }
    };

    const stopListening = () => {
        if (recognitionRef.current) {
            recognitionRef.current.stop();
        }
    };

    const handleVoiceSubmit = async () => {
        if (!transcript.trim()) {
            setError('Please say something first');
            return;
        }

        setIsProcessing(true);
        setError('');

        try {
            // Build conversation context
            const fullContext = buildConversationContext();
            
            const createdTasks = await apiService.createTasksFromVoice(transcript, fullContext);
            
            if (createdTasks && createdTasks.length > 0) {
                // Add this session to conversation history
                setConversationHistory(prev => [...prev, {
                    timestamp: new Date().toISOString(),
                    input: transcript,
                    context: fullContext,
                    tasks: createdTasks
                }]);
                
                setTranscript('');
                setCurrentSession('');
                if (onTasksCreated) {
                    onTasksCreated(createdTasks);
                }
            } else {
                setError('No tasks were created from your voice input');
            }
        } catch (error) {
            console.error('Error creating tasks from voice:', error);
            setError(error.message || 'Failed to create tasks from voice input');
            if (onError) {
                onError(error);
            }
        } finally {
            setIsProcessing(false);
        }
    };

    const buildConversationContext = () => {
        // Build a comprehensive context from conversation history
        let context = '';
        
        if (conversationHistory.length > 0) {
            context += 'Previous conversation context:\n';
            conversationHistory.forEach((entry, index) => {
                context += `${index + 1}. "${entry.input}" (created ${entry.tasks.length} tasks)\n`;
            });
            context += '\n';
        }
        
        if (currentSession) {
            context += `Current session: "${currentSession}"\n`;
        }
        
        // Add local timezone and time information
        const now = new Date();
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        const localTime = now.toLocaleString('en-US', {
            timeZone: timezone,
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            weekday: 'long'
        });
        
        context += `\nLOCAL TIME INFORMATION:\n`;
        context += `Timezone: ${timezone}\n`;
        context += `Local Date/Time: ${localTime}\n`;
        context += `ISO String: ${now.toISOString()}\n`;
        context += `Unix Timestamp: ${Math.floor(now.getTime() / 1000)}\n`;
        
        return context;
    };

    const toggleListening = () => {
        if (isListening) {
            stopListening();
        } else {
            startListening();
        }
    };

    const clearTranscript = () => {
        setTranscript('');
        setError('');
        setCurrentSession('');
    };

    const clearConversationHistory = () => {
        setConversationHistory([]);
        setTranscript('');
        setCurrentSession('');
        setError('');
    };

    if (error && error.includes('not supported')) {
        return (
            <div className="voice-input-container">
                <div className="voice-error">
                    <MicOff size={24} />
                    <p>Voice recognition is not supported in this browser</p>
                </div>
            </div>
        );
    }

    return (
        <div className="voice-input-container">
            <div className="voice-controls">
                <button
                    type="button"
                    className={`voice-button ${isListening ? 'listening' : ''}`}
                    onClick={toggleListening}
                    disabled={isProcessing}
                    aria-label={isListening ? 'Stop listening' : 'Start listening'}
                >
                    {isProcessing ? (
                        <Loader size={18} className="spinning" />
                    ) : isListening ? (
                        <MicOff size={18} />
                    ) : (
                        <Mic size={18} />
                    )}
                    {isListening ? 'Stop' : 'Voice'}
                </button>

                {transcript && (
                    <>
                        <button
                            type="button"
                            className="submit-voice-button"
                            onClick={handleVoiceSubmit}
                            disabled={isProcessing}
                        >
                            {isProcessing ? 'Creating Tasks...' : 'Create Tasks'}
                        </button>
                        <button
                            type="button"
                            className="clear-voice-button"
                            onClick={clearTranscript}
                            disabled={isProcessing}
                        >
                            Clear
                        </button>
                    </>
                )}

                {conversationHistory.length > 0 && (
                    <button
                        type="button"
                        className="clear-history-button"
                        onClick={clearConversationHistory}
                        disabled={isProcessing}
                    >
                        Clear History
                    </button>
                )}
            </div>

            {/* Hidden transcript - only show if there's an error or processing */}
            {error && (
                <div className="voice-error">
                    <p>{error}</p>
                </div>
            )}

            {isListening && (
                <div className="listening-indicator">
                    <div className="pulse-dot"></div>
                    <p>Listening... Speak now (will continue until you stop or pause for 10 seconds)</p>
                </div>
            )}

            {/* Hidden conversation history - only for debugging if needed */}
            {process.env.NODE_ENV === 'development' && conversationHistory.length > 0 && (
                <div className="conversation-history" style={{ display: 'none' }}>
                    <h4>Conversation History ({conversationHistory.length} sessions):</h4>
                    <div className="history-items">
                        {conversationHistory.map((entry, index) => (
                            <div key={index} className="history-item">
                                <div className="history-input">
                                    <strong>Input:</strong> "{entry.input}"
                                </div>
                                <div className="history-tasks">
                                    <strong>Created:</strong> {entry.tasks.length} task(s)
                                </div>
                                <div className="history-time">
                                    {new Date(entry.timestamp).toLocaleTimeString()}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default VoiceInput; 