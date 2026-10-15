/**
 * Main Application Module
 * Orchestrates all components and handles application flow
 */

// The same forgiving comparison as the server's (backend/app/answers.py):
// case, spacing, punctuation and missing Polish letters don't count.
function normalizeAnswer(text) {
    return text.replace(/ł/g, 'l').replace(/Ł/g, 'L')
        .normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
        .toLowerCase().replace(/[^\p{L}\p{N}\s]/gu, ' ')
        .split(/\s+/).filter(Boolean).join(' ');
}

class AphasiaApp {
    constructor() {
        this.currentSession = null;
        this.currentExercises = [];
        this.currentExerciseIndex = 0;
        this.exerciseStartTime = null;
        this.recordedAudio = null;
    }

    init() {
        // Load theme and text size
        ui.loadTheme();
        this.setLargeText(localStorage.getItem('textSize') === 'large');

        // The login is an httpOnly cookie, so ask the server whether there is one.
        this.loadUserData();

        // Set up event listeners
        this.setupEventListeners();
        ui.addReadAloudButtons();

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
        [['consent-recordings', 'recordings'], ['consent-speech', 'speech_recognition']].forEach(([id, kind]) => {
            document.getElementById(id).addEventListener('change', async (e) => {
                await this.saveConsent(kind, e.target.checked);
            });
        });

        document.getElementById('download-data').addEventListener('click', async () => {
            try {
                ui.downloadFile(await api.exportMyData(), 'afasia-my-data.json');
            } catch {
                ui.showFormMessage('data-message', 'error', 'error');
            }
        });

        const deleteDialog = document.getElementById('delete-dialog');
        document.getElementById('delete-account').addEventListener('click', () => {
            deleteDialog.showModal();
            document.getElementById('delete-password').focus();
        });
        document.getElementById('delete-cancel').addEventListener('click', () => deleteDialog.close());
        // However it closes (Cancel, Escape, or done), nothing typed stays behind.
        deleteDialog.addEventListener('close', () => {
            document.getElementById('delete-form').reset();
            ui.clearFormMessage('delete-message');
        });
        document.getElementById('delete-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleDeleteAccount();
        });

        document.getElementById('try-again').addEventListener('click', () => this.tryAgain());
        document.getElementById('choose-words').addEventListener('click', () => this.showWordChoices());

        document.getElementById('next-exercise').addEventListener('click', () => {
            this.goToNextExercise();
        });

        document.getElementById('hint-btn').addEventListener('click', async () => {
            await this.showNextHint();
        });

        document.getElementById('password-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleChangePassword();
        });

        document.getElementById('account-logout').addEventListener('click', () => {
            this.logout();
        });

        document.getElementById('logout-btn').addEventListener('click', () => {
            this.logout();
        });

        // Language toggle
        document.getElementById('lang-toggle').addEventListener('click', () => {
            const currentLang = i18n.getCurrentLanguage();
            const newLang = currentLang === 'en' ? 'pl' : 'en';
            i18n.setLanguage(newLang);
            ui.updateReadAloud();
        });

        // Read aloud (U3): the question and the feedback.
        document.getElementById('read-question').addEventListener('click', () => {
            reader.read(document.getElementById('exercise-question-text').textContent, i18n.getCurrentLanguage());
        });
        document.getElementById('read-feedback').addEventListener('click', () => {
            reader.read(document.getElementById('feedback').textContent, i18n.getCurrentLanguage());
        });
        if ('speechSynthesis' in window) {
            speechSynthesis.addEventListener('voiceschanged', () => ui.updateReadAloud());
        }

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
                } else if (page === 'account') {
                    ui.showPage('account');
                    this.showConsents();
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
        document.getElementById('exit-exercise').addEventListener('click', async () => {
            if (await ui.confirmLeave()) {
                this.exitExercise();
            }
        });

        document.getElementById('app-message-ok').addEventListener('click', () => ui.clearNotice());

        document.getElementById('text-size').addEventListener('click', () => {
            const large = !document.documentElement.classList.contains('large-text');
            this.setLargeText(large);
            localStorage.setItem('textSize', large ? 'large' : 'normal');
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
                ui.notify('exportFailed');
            }
        });

        document.getElementById('export-pdf')?.addEventListener('click', async () => {
            try {
                const blob = await api.exportProgressPDF();
                ui.downloadFile(blob, `progress_${new Date().toISOString().split('T')[0]}.pdf`);
            } catch (error) {
                ui.notify('exportFailed');
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
            const key = { 401: 'loginFailed', 400: 'accountInactive', 429: 'tooManyAttempts' }[error.status] || 'tryAgain';
            ui.showFormMessage('login-message', key, 'error');
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
            const key = { 400: 'accountTaken', 422: 'signUpCheck' }[error.status] || 'tryAgain';
            ui.showFormMessage('register-message', key, 'error');
        }
    }

    // The person's consent answers, loaded once per login.
    async loadConsents() {
        if (!this.consents) {
            this.consents = await api.getConsents();
        }
        return this.consents;
    }

    // Whether the person agrees to `kind`, asking them first if they haven't
    // been asked yet. A dialog closed without an answer counts as no, and is
    // not saved, so they are asked again next time.
    async hasConsent(kind) {
        let consents;
        try {
            consents = await this.loadConsents();
        } catch {
            return false;
        }
        if (consents[kind] !== null) {
            return consents[kind];
        }
        const answer = await ui.askConsent(kind);
        if (answer === null) {
            return false;
        }
        await this.saveConsent(kind, answer);
        return answer;
    }

    async saveConsent(kind, granted) {
        try {
            this.consents = await api.setConsents({ [kind]: granted });
            ui.showFormMessage('consent-message', 'saved', 'success');
        } catch {
            ui.showFormMessage('consent-message', 'error', 'error');
        }
    }

    async showConsents() {
        try {
            const consents = await this.loadConsents();
            document.getElementById('consent-recordings').checked = consents.recordings === true;
            document.getElementById('consent-speech').checked = consents.speech_recognition === true;
        } catch {
            ui.showFormMessage('consent-message', 'error', 'error');
        }
    }

    async handleDeleteAccount() {
        try {
            await api.deleteAccount(document.getElementById('delete-password').value);
        } catch (error) {
            const key = { 400: 'passwordNotRight', 429: 'tooManyAttempts' }[error.status] || 'error';
            ui.showFormMessage('delete-message', key, 'error');
            return;
        }
        document.getElementById('delete-dialog').close();
        this.leaveExercise();
        this.consents = null;
        ui.showAuthPage();
    }

    async showNextHint() {
        const button = document.getElementById('hint-btn');
        const exercise = this.currentExercises[this.currentExerciseIndex];
        button.disabled = true;  // one request at a time
        try {
            const hint = await api.getHint(exercise.id);
            const item = el('li');
            item.append(el('span', '', hint.cue), ' ', ui.readAloudButton(() => hint.cue));
            document.getElementById('hint-list').append(item);
            button.disabled = hint.last;
        } catch (error) {
            // No more hints, or the exercise was answered meanwhile.
            console.error('Hint failed:', error);
        }
    }

    async handleChangePassword() {
        const form = document.getElementById('password-form');
        const current = document.getElementById('current-password').value;
        const next = document.getElementById('new-password').value;
        try {
            await api.changePassword(current, next);
            form.reset();
            ui.showFormMessage('password-message', 'passwordChanged', 'success');
        } catch (error) {
            const key = {
                400: 'wrongCurrentPassword', 422: 'newPasswordRules', 429: 'tooManyAttempts',
            }[error.status] || 'error';
            ui.showFormMessage('password-message', key, 'error');
        }
    }

    async logout() {
        this.leaveExercise();
        this.consents = null;  // the next person's answers are their own
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
            ui.notify('scheduleFailed');
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
        } catch (error) {
            ui.notify('startFailed');
        }
    }

    showCurrentExercise() {
        const exercise = this.currentExercises[this.currentExerciseIndex];
        if (!exercise) return;

        this.exerciseStartTime = Date.now();

        // Start clean: nothing typed or recorded for an earlier exercise is
        // kept, and Submit works again.
        this.recordedAudio = null;
        this.stopListening();
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
        document.getElementById('read-feedback').style.display = 'none';
        document.getElementById('next-exercise').style.display = 'none';
        document.getElementById('try-again').style.display = 'none';
        this.practiceAnswer = null;
        this.lastRightAnswer = null;
        ui.updateReadAloud();
        document.getElementById('submit-answer').style.display = '';

        // The question first, for keyboard and screen-reader users.
        ui.focusHeading(document.getElementById('exercise-question-text'));

        // Hints: for naming only, starting afresh for every exercise.
        document.getElementById('hint-list').replaceChildren();
        document.getElementById('hint-btn').disabled = false;
        document.getElementById('hint-area').style.display =
            exercise.exercise_type === 'word_naming' ? 'block' : 'none';

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

        document.getElementById('exercise-options').replaceChildren();
        document.getElementById('choose-words').hidden = false;
        if (exercise.options && exercise.options.length > 0) {
            // Multiple choice
            this.showOptions(exercise.options);
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
        const selectedOption = document.querySelector('#exercise-options .option-btn.selected');
        if (exercise.options && exercise.options.length > 0) {
            answer = selectedOption ? selectedOption.dataset.answer : '';
        } else if (selectedOption) {
            answer = selectedOption.dataset.answer;  // a naming word chosen from the list
        } else if (exercise.exercise_type === 'pronunciation') {
            if (this.recordedAudio) {
                // There is a recording only with consent to keep it (P1-6b).
                await api.uploadAudio(exercise.id, this.recordedAudio).catch((error) => {
                    console.error('Upload failed:', error);
                });
                // Speech recognition needs its own consent: the browser may
                // send the audio to its maker's servers.
                if (speechRecognizer.isSupported() && await this.hasConsent('speech_recognition')) {
                    try {
                        const result = await speechRecognizer.recognize(
                            i18n.getCurrentLanguage() === 'pl' ? 'pl-PL' : 'en-US'
                        );
                        answer = result.transcript;
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

        // A practice try after a wrong answer: checked here against the answer
        // already shown, never sent or scored (the first answer counts).
        if (answer && this.practiceAnswer) {
            this.checkPracticeAnswer(answer);
            return;
        }

        if (!answer) {
            submitButton.disabled = false;
            const feedback = document.getElementById('feedback');
            feedback.className = 'feedback';
            feedback.textContent = i18n.translate('answerFirst');
            feedback.style.display = 'block';
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
                if (result.cue_level > 0) {
                    feedback.append(` ${i18n.translate('hintsUsed')}: ${result.cue_level}`);
                }
            } else {
                // One calm message, with the right answer emphasized; "almost"
                // for a near miss (the server decides, app/answers.py).
                const text = result.almost
                    ? i18n.translate('almostRight')
                    : `${i18n.translate('incorrect')} ${i18n.translate('correctAnswer')}:`;
                this.showFeedback('incorrect', text, result.correct_answer);
            }
            // Practice once more after a wrong answer (not for recordings).
            this.lastRightAnswer = result.is_correct || exercise.exercise_type === 'pronunciation'
                ? null : result.correct_answer;
            this.offerNext();
        } catch (error) {
            submitButton.disabled = false;
            ui.notify('answerFailed');
        }
    }

    async toggleRecording() {
        const recordBtn = document.getElementById('record-btn');
        const statusEl = document.getElementById('recording-status');

        if (!audioRecorder.isRecording) {
            // Start recording (ignoring clicks while asking or while the
            // microphone opens). Without consent the microphone stays off.
            if (this.openingMicrophone) return;
            this.openingMicrophone = true;
            const allowed = await this.hasConsent('recordings');
            const started = allowed && await audioRecorder.startRecording();
            this.openingMicrophone = false;
            if (!allowed) {
                statusEl.textContent = i18n.translate('recordingOff');
                return;
            }
            if (!started) {
                statusEl.textContent = i18n.translate('microphoneBlocked');
                return;
            }

            recordBtn.classList.add('recording');
            recordBtn.replaceChildren(el('span', 'record-icon', '⏹️'), el('span', '', 'Stop'));
            statusEl.textContent = 'Recording...';
        } else {
            // Stop recording
            this.recordedAudio = await audioRecorder.stopRecording();
            this.resetRecordButton();
            statusEl.textContent = 'Recording saved. Click submit when ready.';
        }
    }

    resetRecordButton() {
        const recordBtn = document.getElementById('record-btn');
        recordBtn.classList.remove('recording');
        const label = el('span', '', i18n.translate('record'));
        label.dataset.i18n = 'record';
        recordBtn.replaceChildren(el('span', 'record-icon', '🎤'), label);
    }

    // Turn the microphone off and forget any unfinished recording.
    stopListening() {
        audioRecorder.cleanup();
        speechRecognizer.stop();
        this.resetRecordButton();
    }

    async completeSession() {
        try {
            // The server scored the session when the last answer arrived.
            const session = await api.completeSession(this.currentSession.id);

            this.stopListening();

            // Back to the dashboard, with the result in words.
            ui.showPage('dashboard');
            ui.loadRecentSessions();
            await this.loadUserData();
            ui.notify('sessionDone', 'status', { score: Math.round(session.score) });
        } catch (error) {
            console.error('Failed to complete session:', error);
        }
    }

    exitExercise() {
        this.leaveExercise();
        ui.showPage('dashboard');
    }

    leaveExercise() {
        this.stopListening();
    }

    // Larger text (U1): everything is sized in rem, so the root size scales it all.
    setLargeText(large) {
        document.documentElement.classList.toggle('large-text', large);
        document.getElementById('text-size').setAttribute('aria-pressed', String(large));
    }

    // Answer buttons: one can be selected at a time.
    showOptions(options) {
        const optionsContainer = document.getElementById('exercise-options');
        optionsContainer.style.display = 'grid';
        optionsContainer.replaceChildren(...options.map((option) => {
            const button = el('button', 'option-btn', option);
            button.type = 'button';
            button.dataset.answer = option;
            button.addEventListener('click', () => {
                optionsContainer.querySelectorAll('.option-btn').forEach((b) => b.classList.remove('selected'));
                button.classList.add('selected');
            });
            return button;
        }));
    }

    // Naming without typing (U6): show words to choose from.
    async showWordChoices() {
        const exercise = this.currentExercises[this.currentExerciseIndex];
        const button = document.getElementById('choose-words');
        button.disabled = true;
        try {
            const { choices } = await api.getChoices(exercise.id);
            this.showOptions(choices);
            button.hidden = true;
        } catch (error) {
            console.error('Choices failed:', error);
        } finally {
            button.disabled = false;
        }
    }

    showFeedback(kind, text, answer = null) {
        const feedback = document.getElementById('feedback');
        feedback.style.display = 'block';
        feedback.className = `feedback ${kind}`;
        feedback.textContent = text;
        if (answer) {
            const strong = document.createElement('strong');
            strong.textContent = answer;
            feedback.append(' ', strong);
        }
    }

    // After an answer: "Next" (or the result after the last exercise), with
    // the focus on it (U4), and "Try again" after a wrong one (U8).
    offerNext() {
        const last = this.currentExerciseIndex === this.currentExercises.length - 1;
        const next = document.getElementById('next-exercise');
        next.dataset.i18n = last ? 'seeResult' : 'nextExercise';
        next.textContent = i18n.translate(next.dataset.i18n);
        document.getElementById('submit-answer').style.display = 'none';
        document.getElementById('hint-area').style.display = 'none';  // no hints once answered
        document.getElementById('read-feedback').style.display = '';
        document.getElementById('try-again').style.display = this.lastRightAnswer ? 'inline-block' : 'none';
        next.style.display = 'inline-block';
        next.focus();
        ui.updateReadAloud();
    }

    tryAgain() {
        this.practiceAnswer = this.lastRightAnswer;
        document.getElementById('try-again').style.display = 'none';
        document.getElementById('next-exercise').style.display = 'none';
        const submit = document.getElementById('submit-answer');
        submit.style.display = '';
        submit.disabled = false;
        document.getElementById('answer-input').value = '';
        document.querySelectorAll('.option-btn').forEach((b) => b.classList.remove('selected'));
        const input = document.getElementById('answer-input');
        (input.offsetParent ? input : document.querySelector('.option-btn'))?.focus();
    }

    checkPracticeAnswer(answer) {
        const right = this.practiceAnswer;
        this.practiceAnswer = null;
        if (normalizeAnswer(answer) === normalizeAnswer(right)) {
            this.showFeedback('correct', i18n.translate('practiceRight'));
            this.lastRightAnswer = null;
        } else {
            this.showFeedback('incorrect', i18n.translate('practiceWrong'), right);
        }
        this.offerNext();
    }

    goToNextExercise() {
        this.currentExerciseIndex++;
        if (this.currentExerciseIndex < this.currentExercises.length) {
            this.showCurrentExercise();
        } else {
            this.completeSession();
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
