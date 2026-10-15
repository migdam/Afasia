/**
 * Main Application Module
 * Orchestrates all components and handles application flow
 */

class AphasiaApp {
    constructor() {
        this.currentSession = null;
        this.currentExercises = [];
        this.currentExerciseIndex = 0;
        this.exerciseStartTime = null;
        this.timerInterval = null;
        this.advanceTimeout = null;
        this.recordedAudio = null;
    }

    init() {
        // Load theme
        ui.loadTheme();

        // The login is an httpOnly cookie, so ask the server whether there is one.
        this.loadUserData();

        // Set up event listeners
        this.setupEventListeners();

        // Initialize i18n
        i18n.updatePageTranslations();
    }

    async loadUserData() {
        try {
            const user = await api.getProfile();
            ui.showDashboard(user);
            ui.loadRecentSessions();
            ui.loadScheduledSessions();
        } catch (error) {
            console.error('Failed to load user data:', error);
            ui.showAuthPage();
        }
    }

    setupEventListeners() {
        // Auth forms
        document.getElementById('show-register').addEventListener('click', (e) => {
            e.preventDefault();
            document.getElementById('login-form').style.display = 'none';
            document.getElementById('register-form').style.display = 'block';
        });

        document.getElementById('show-login').addEventListener('click', (e) => {
            e.preventDefault();
            document.getElementById('register-form').style.display = 'none';
            document.getElementById('login-form').style.display = 'block';
        });

        document.getElementById('login-form-submit').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleLogin();
        });

        document.getElementById('register-form-submit').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleRegister();
        });

        // Logout
        document.getElementById('logout-btn').addEventListener('click', () => {
            this.logout();
        });

        // Language toggle
        document.getElementById('lang-toggle').addEventListener('click', () => {
            const currentLang = i18n.getCurrentLanguage();
            const newLang = currentLang === 'en' ? 'pl' : 'en';
            i18n.setLanguage(newLang);
        });

        // Theme toggle (Enhancement 7)
        document.getElementById('theme-toggle').addEventListener('click', () => {
            ui.toggleDarkMode();
        });

        // Bottom navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                const page = item.getAttribute('data-page');
                if (page === 'dashboard') {
                    ui.showPage('dashboard');
                    ui.loadRecentSessions();
                    ui.loadScheduledSessions();
                } else if (page === 'progress') {
                    ui.showPage('progress');
                    ui.loadProgress();
                } else if (page === 'admin') {
                    ui.showPage('admin');
                    ui.loadAdminDashboard();
                }
            });
        });

        // New session form
        document.getElementById('new-session-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.startNewSession();
        });

        // Schedule modal
        document.getElementById('add-schedule-btn').addEventListener('click', () => {
            ui.showModal('schedule-modal');
        });

        document.querySelectorAll('.modal-close, .modal-cancel').forEach(btn => {
            btn.addEventListener('click', () => {
                ui.hideModal('schedule-modal');
            });
        });

        document.getElementById('schedule-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleScheduleSession();
        });

        // Exercise controls
        document.getElementById('exit-exercise').addEventListener('click', () => {
            if (confirm('Are you sure you want to exit? Progress will be lost.')) {
                this.exitExercise();
            }
        });

        document.getElementById('submit-answer').addEventListener('click', () => {
            this.submitCurrentAnswer();
        });

        // Audio playback
        document.getElementById('play-audio-btn')?.addEventListener('click', () => {
            const audioUrl = document.getElementById('play-audio-btn').dataset.url;
            if (audioUrl) {
                audioPlayer.play(audioUrl);
            }
        });

        // Voice recording (Enhancement 1)
        document.getElementById('record-btn')?.addEventListener('click', async () => {
            await this.toggleRecording();
        });

        // Export buttons (Enhancement 9)
        document.getElementById('export-csv')?.addEventListener('click', async () => {
            try {
                const blob = await api.exportProgressCSV();
                ui.downloadFile(blob, `progress_${new Date().toISOString().split('T')[0]}.csv`);
            } catch (error) {
                alert('Failed to export CSV');
            }
        });

        document.getElementById('export-pdf')?.addEventListener('click', async () => {
            try {
                const blob = await api.exportProgressPDF();
                ui.downloadFile(blob, `progress_${new Date().toISOString().split('T')[0]}.pdf`);
            } catch (error) {
                alert('Failed to export PDF');
            }
        });
    }

    async handleLogin() {
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        try {
            const response = await api.login({ username, password });
            ui.showDashboard(response.user);
            ui.loadRecentSessions();
            ui.loadScheduledSessions();
        } catch (error) {
            alert('Login failed: ' + error.message);
        }
    }

    async handleRegister() {
        const email = document.getElementById('register-email').value;
        const username = document.getElementById('register-username').value;
        const password = document.getElementById('register-password').value;
        const fullName = document.getElementById('register-fullname').value;

        try {
            const response = await api.register({
                email,
                username,
                password,
                full_name: fullName,
                language: i18n.getCurrentLanguage(),
            });
            ui.showDashboard(response.user);
            ui.loadRecentSessions();
            ui.loadScheduledSessions();
        } catch (error) {
            alert('Registration failed: ' + error.message);
        }
    }

    async logout() {
        // Wait until the cookie is gone, or it could outlive a new login.
        await api.logout();
        ui.showAuthPage();
    }

    async handleScheduleSession() {
        const title = document.getElementById('schedule-title').value;
        const datetime = document.getElementById('schedule-datetime').value;
        const exerciseType = document.getElementById('schedule-type').value;
        const difficulty = document.getElementById('schedule-difficulty').value;

        try {
            await api.createScheduledSession({
                title,
                scheduled_time: new Date(datetime).toISOString(),
                exercise_type: exerciseType,
                difficulty,
            });

            ui.hideModal('schedule-modal');
            ui.loadScheduledSessions();
            document.getElementById('schedule-form').reset();
        } catch (error) {
            alert('Failed to schedule session');
        }
    }

    async startNewSession() {
        const exerciseType = document.getElementById('exercise-type').value;
        const difficulty = document.getElementById('difficulty').value;
        const numExercises = parseInt(document.getElementById('num-exercises').value);

        try {
            // Create session
            this.currentSession = await api.createSession({
                title: `${exerciseType} - ${difficulty}`,
                exercise_type: exerciseType,
                difficulty: difficulty,
                language: i18n.getCurrentLanguage(),
                num_exercises: numExercises,
            });

            // Load exercises
            this.currentExercises = await api.getExercises(this.currentSession.id);
            this.currentExerciseIndex = 0;

            // Show exercise page
            ui.showPage('exercise');
            this.showCurrentExercise();
            this.startTimer();
        } catch (error) {
            alert('Failed to start session: ' + error.message);
        }
    }

    showCurrentExercise() {
        const exercise = this.currentExercises[this.currentExerciseIndex];
        if (!exercise) return;

        this.exerciseStartTime = Date.now();

        // Start clean: nothing typed or recorded for an earlier exercise is
        // kept, and Submit works again.
        this.recordedAudio = null;
        document.getElementById('answer-input').value = '';
        document.getElementById('submit-answer').disabled = false;

        // Update progress
        document.getElementById('exercise-counter').textContent =
            `${this.currentExerciseIndex + 1}/${this.currentExercises.length}`;

        const progress = ((this.currentExerciseIndex) / this.currentExercises.length) * 100;
        document.getElementById('progress-fill').style.width = `${progress}%`;

        // Show question
        document.getElementById('exercise-question-text').textContent = exercise.question;

        // Hide all input types
        document.getElementById('exercise-image').style.display = 'none';
        document.getElementById('exercise-audio').style.display = 'none';
        document.getElementById('exercise-options').style.display = 'none';
        document.getElementById('exercise-input').style.display = 'none';
        document.getElementById('voice-recorder').style.display = 'none';
        document.getElementById('feedback').style.display = 'none';

        // Show appropriate input based on exercise type
        if (exercise.image_url) {
            // Image-based exercise (Enhancement 2)
            document.getElementById('exercise-image').style.display = 'block';
            document.getElementById('exercise-img').src = exercise.image_url;
        }

        if (exercise.audio_url) {
            // Audio exercise (Enhancement 6)
            document.getElementById('exercise-audio').style.display = 'block';
            document.getElementById('play-audio-btn').dataset.url = exercise.audio_url;
        }

        if (exercise.options && exercise.options.length > 0) {
            // Multiple choice
            const optionsContainer = document.getElementById('exercise-options');
            optionsContainer.style.display = 'grid';
            optionsContainer.replaceChildren(...exercise.options.map(option => {
                const button = el('button', 'option-btn', option);
                button.dataset.answer = option;
                return button;
            }));

            // Add click handlers
            optionsContainer.querySelectorAll('.option-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    optionsContainer.querySelectorAll('.option-btn').forEach(b =>
                        b.classList.remove('selected'));
                    btn.classList.add('selected');
                });
            });
        } else if (exercise.exercise_type === 'pronunciation') {
            // Voice recording (Enhancement 1 & 12)
            document.getElementById('voice-recorder').style.display = 'block';
            document.getElementById('recording-status').textContent = '';
        } else {
            // Text input
            document.getElementById('exercise-input').style.display = 'block';
            document.getElementById('answer-input').focus();
        }
    }

    async submitCurrentAnswer() {
        const exercise = this.currentExercises[this.currentExerciseIndex];
        const submitButton = document.getElementById('submit-answer');
        // One submission per exercise: Submit stays off until the next one
        // is shown, so a double click can't send the answer twice.
        submitButton.disabled = true;
        let answer = '';

        // Read the answer from the input this exercise shows, never from a
        // hidden one that still holds an earlier value.
        if (exercise.options && exercise.options.length > 0) {
            const selectedOption = document.querySelector('.option-btn.selected');
            answer = selectedOption ? selectedOption.dataset.answer : '';
        } else if (exercise.exercise_type === 'pronunciation') {
            if (this.recordedAudio) {
                // Use speech recognition if available (Enhancement 12)
                if (speechRecognizer.isSupported()) {
                    try {
                        const result = await speechRecognizer.recognize(
                            i18n.getCurrentLanguage() === 'pl' ? 'pl-PL' : 'en-US'
                        );
                        answer = result.transcript;

                        // Upload audio
                        await api.uploadAudio(exercise.id, this.recordedAudio);
                    } catch (error) {
                        console.error('Speech recognition failed:', error);
                        answer = 'recognition_failed';
                    }
                } else {
                    answer = 'recorded';
                }
            }
        } else {
            answer = document.getElementById('answer-input').value;
        }

        if (!answer) {
            submitButton.disabled = false;
            alert('Please provide an answer');
            return;
        }

        const timeTaken = Math.floor((Date.now() - this.exerciseStartTime) / 1000);

        try {
            const result = await api.submitAnswer(exercise.id, answer, timeTaken);

            // Show feedback
            const feedback = document.getElementById('feedback');
            feedback.style.display = 'block';

            if (result.is_correct) {
                feedback.className = 'feedback correct';
                feedback.textContent = i18n.translate('correct');
            } else {
                // One calm message, with the right answer emphasized.
                feedback.className = 'feedback incorrect';
                feedback.textContent = `${i18n.translate('incorrect')} ${i18n.translate('correctAnswer')}: `;
                const rightAnswer = document.createElement('strong');
                rightAnswer.textContent = result.correct_answer;
                feedback.append(rightAnswer);
            }

            // Move to next exercise after delay
            this.advanceTimeout = setTimeout(() => {
                this.advanceTimeout = null;
                this.currentExerciseIndex++;
                if (this.currentExerciseIndex < this.currentExercises.length) {
                    this.showCurrentExercise();
                } else {
                    this.completeSession();
                }
            }, 2000);
        } catch (error) {
            submitButton.disabled = false;
            alert('Failed to submit answer: ' + error.message);
        }
    }

    async toggleRecording() {
        const recordBtn = document.getElementById('record-btn');
        const statusEl = document.getElementById('recording-status');

        if (!audioRecorder.isRecording) {
            // Start recording
            const initialized = audioRecorder.stream || await audioRecorder.init();
            if (!initialized) return;

            audioRecorder.startRecording();
            recordBtn.classList.add('recording');
            recordBtn.replaceChildren(el('span', 'record-icon', '⏹️'), el('span', '', 'Stop'));
            statusEl.textContent = 'Recording...';
        } else {
            // Stop recording
            this.recordedAudio = await audioRecorder.stopRecording();
            recordBtn.classList.remove('recording');
            const label = el('span', '', i18n.translate('record'));
            label.dataset.i18n = 'record';
            recordBtn.replaceChildren(el('span', 'record-icon', '🎤'), label);
            statusEl.textContent = 'Recording saved. Click submit when ready.';
        }
    }

    async completeSession() {
        try {
            // The server scored the session when the last answer arrived.
            const session = await api.completeSession(this.currentSession.id);

            this.stopTimer();
            alert(`Session complete! Score: ${Math.round(session.score)}%`);

            // Return to dashboard
            ui.showPage('dashboard');
            ui.loadRecentSessions();
            this.loadUserData();
        } catch (error) {
            console.error('Failed to complete session:', error);
        }
    }

    exitExercise() {
        // A pending move to the next exercise would otherwise run in the
        // next session.
        clearTimeout(this.advanceTimeout);
        this.advanceTimeout = null;
        this.stopTimer();
        ui.showPage('dashboard');
    }

    startTimer() {
        let seconds = 0;
        const timerEl = document.getElementById('exercise-timer');

        this.timerInterval = setInterval(() => {
            seconds++;
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            timerEl.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }, 1000);
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new AphasiaApp();
    app.init();

    // Make app globally accessible for debugging
    window.app = app;
});
