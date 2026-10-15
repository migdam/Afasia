/**
 * Audio Module
 * Handles audio recording and playback for pronunciation exercises
 */

class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.stream = null;
        this.isRecording = false;
    }

    // The microphone is opened for each recording and released as soon as it
    // ends, so the browser shows it in use only while someone is recording.
    async startRecording() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        } catch (error) {
            // The caller explains this in words (app.toggleRecording).
            console.error('Microphone access denied:', error);
            return false;
        }

        this.audioChunks = [];
        this.mediaRecorder = new MediaRecorder(this.stream);

        this.mediaRecorder.ondataavailable = (event) => {
            this.audioChunks.push(event.data);
        };

        this.mediaRecorder.start();
        this.isRecording = true;
        return true;
    }

    stopRecording() {
        return new Promise((resolve) => {
            if (!this.mediaRecorder || !this.isRecording) {
                resolve(null);
                return;
            }

            this.mediaRecorder.onstop = () => {
                // Keep the format the browser really recorded (WebM or MP4, not WAV).
                const audioBlob = new Blob(this.audioChunks, { type: this.mediaRecorder.mimeType || 'audio/webm' });
                this.isRecording = false;
                this.releaseMicrophone();
                resolve(audioBlob);
            };

            this.mediaRecorder.stop();
        });
    }

    async playAudioBlob(blob) {
        const audioUrl = URL.createObjectURL(blob);
        const audio = new Audio(audioUrl);
        await audio.play();
    }

    releaseMicrophone() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
    }

    // Drop any recording in progress and turn the microphone off: when
    // leaving an exercise, a session, or the app.
    cleanup() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.onstop = null;
            this.mediaRecorder.stop();
        }
        this.isRecording = false;
        this.audioChunks = [];
        this.releaseMicrophone();
    }
}

class AudioPlayer {
    constructor() {
        this.currentAudio = null;
    }

    play(url) {
        // Stop current audio if playing
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio.currentTime = 0;
        }

        this.currentAudio = new Audio(url);
        return this.currentAudio.play();
    }

    stop() {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio.currentTime = 0;
        }
    }
}

// Web Speech API for speech recognition (Enhancement 12)
class SpeechRecognizer {
    constructor() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (SpeechRecognition) {
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
        } else {
            this.recognition = null;
            console.warn('Speech recognition not supported');
        }
    }

    isSupported() {
        return this.recognition !== null;
    }

    async recognize(lang = 'en-US') {
        if (!this.recognition) {
            throw new Error('Speech recognition not supported');
        }

        return new Promise((resolve, reject) => {
            this.recognition.lang = lang;

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                const confidence = event.results[0][0].confidence;
                resolve({ transcript, confidence });
            };

            this.recognition.onerror = (event) => {
                reject(event.error);
            };

            this.recognition.start();
        });
    }

    stop() {
        if (this.recognition) {
            this.recognition.stop();
        }
    }
}

// Create global instances
const audioRecorder = new AudioRecorder();
const audioPlayer = new AudioPlayer();
const speechRecognizer = new SpeechRecognizer();
