/**
 * Internationalization (i18n) module
 * Supports English and Polish languages
 */

const translations = {
    en: {
        // Navigation & Auth
        welcome: "Welcome to Aphasia Therapy",
        subtitle: "Interactive speech therapy exercises",
        login: "Login",
        register: "Register",
        logout: "Logout",
        username: "Username",
        password: "Password",
        email: "Email",
        fullName: "Full Name",
        noAccount: "Don't have an account?",
        haveAccount: "Already have an account?",

        // Dashboard
        dashboard: "Dashboard",
        points: "Points",
        streak: "Streak",
        badges: "Badges",
        startSession: "Start New Session",
        exerciseType: "Exercise Type",
        difficulty: "Difficulty",
        numExercises: "Number of Exercises",
        start: "Start",
        scheduledSessions: "Scheduled Sessions",
        addSchedule: "Add Schedule",
        noScheduled: "No scheduled sessions",
        recentSessions: "Recent Sessions",
        noSessions: "No sessions yet",

        // Exercise Types
        wordNaming: "Word Naming",
        sentenceCompletion: "Sentence Completion",
        imageRecognition: "Image Recognition",
        pronunciation: "Pronunciation",

        // Difficulty Levels
        easy: "Easy",
        medium: "Medium",
        hard: "Hard",

        // Exercise Page
        exit: "Exit",
        submit: "Submit",
        record: "Record",
        correct: "Correct! Well done!",
        incorrect: "Not quite.",
        correctAnswer: "Correct answer",
        hint: "Hint",
        chooseWords: "Choose from words",
        useTiles: "Build from letters",
        undo: "Undo",
        space: "space",
        nextExercise: "Next",
        playRecording: "▶ Play my recording",
        howDidItGo: "How did it go?",
        rateSaid: "I said it",
        rateNotYet: "Not yet",
        rateFirst: "Choose how it went first.",
        heard: "The browser heard:",
        keepPractising: "That's all right. Keep practising, it gets easier.",
        tryAgainPractice: "Try again",
        practiceRight: "That's it.",
        practiceWrong: "Not yet. The answer is:",
        almostRight: "Almost. The answer is:",
        largerText: "Larger text",
        readAloud: "Read aloud",

        // Messages in the app (U12)
        ok: "OK",
        tryAgain: "Something went wrong. Please try again in a moment.",
        loginFailed: "The username or password is not right.",
        accountInactive: "This account is turned off. Ask your therapist or administrator.",
        accountTaken: "That username or email is already used. Try another one, or log in.",
        signUpCheck: "Please check the form: the password needs at least 8 characters, and the email must be complete.",
        exportFailed: "The file couldn't be made. Please try again.",
        scheduleFailed: "The plan couldn't be saved. Check the date and try again.",
        startFailed: "The session couldn't start. Please try again.",
        answerFirst: "Choose or type an answer first.",
        answerFailed: "Your answer couldn't be sent. Check your connection and try again.",
        sessionDone: "Session finished. Your score: {score}%.",
        deletePlanFailed: "The plan couldn't be deleted. Please try again.",
        userStatusFailed: "The account couldn't be changed. Please try again.",
        microphoneBlocked: "The microphone is blocked. Allow it in your browser's settings, then try again.",
        leaveTitle: "Leave this session?",
        leaveText: "The session stays unfinished and doesn't count towards your scores.",
        stay: "Stay",
        leave: "Leave",
        seeResult: "See my result",
        hintsUsed: "Hints used",

        // Progress
        myProgress: "My Progress",
        progress: "Progress",
        exportCSV: "Export CSV",
        exportPDF: "Export PDF",
        totalSessions: "Total Sessions",
        avgAccuracy: "Average Accuracy",
        totalTime: "Total Time",
        longestStreak: "Longest Streak",
        progressChart: "Progress Over Time",
        earnedBadges: "Earned Badges",
        noBadges: "No badges yet",

        // Admin
        admin: "Admin",
        adminDashboard: "Admin Dashboard",
        totalUsers: "Total Users",
        activeUsers: "Active Users",
        platformAccuracy: "Platform Accuracy",
        allUsers: "All Users",

        // Modal
        scheduleSession: "Schedule Session",
        title: "Title",
        dateTime: "Date & Time",
        cancel: "Cancel",
        schedule: "Schedule",

        // Account
        account: "Account",
        changePassword: "Change password",
        currentPassword: "Current password",
        newPassword: "New password (at least 8 characters)",
        passwordChanged: "Your password has been changed. You are logged out on your other devices.",
        wrongCurrentPassword: "The current password is not right.",
        newPasswordRules: "The new password needs at least 8 characters.",
        tooManyAttempts: "Too many wrong passwords. Wait up to 15 minutes, then try again.",
        yourChoices: "Your choices",
        consentRecordingsLabel: "Keep my voice recordings",
        consentSpeechLabel: "Use the browser's speech recognition",
        saved: "Saved.",

        // Consent questions
        recordingsConsentTitle: "Keep your recordings?",
        recordingsConsentText: "To practise speaking, the app records your voice. May we keep your recordings on the server? Only you can play them. You can change this at any time on the Account page.",
        recordingsConsentYes: "Yes, keep them",
        speech_recognitionConsentTitle: "Use speech recognition?",
        speech_recognitionConsentText: "Your browser can try to recognise what you said. To do this, it may send your voice to the company that made the browser. It often gets speech wrong when someone has aphasia. You can change this at any time on the Account page.",
        speech_recognitionConsentYes: "Yes, use it",
        consentNo: "No",
        recordingOff: "Recording is off. You can turn it on on the Account page.",

        // Your data
        privacyNotice: "Privacy notice",
        yourData: "Your data",
        yourDataText: "Download everything the app keeps about you, or delete your account.",
        downloadData: "Download my data",
        deleteAccount: "Delete my account",
        deleteTitle: "Delete your account?",
        deleteText: "This deletes your account, your answers, your scores and your recordings. It cannot be undone. Type your password to confirm.",
        deleteForGood: "Delete for good",
        passwordNotRight: "The password is not right.",

        // Common
        save: "Save",
        delete: "Delete",
        edit: "Edit",
        close: "Close",
        loading: "Loading...",
        error: "An error occurred",
        success: "Success",
    },

    pl: {
        // Navigation & Auth
        welcome: "Witamy w Terapii Afazji",
        subtitle: "Interaktywne ćwiczenia logopedyczne",
        login: "Zaloguj się",
        register: "Zarejestruj się",
        logout: "Wyloguj",
        username: "Nazwa użytkownika",
        password: "Hasło",
        email: "E-mail",
        fullName: "Imię i nazwisko",
        noAccount: "Nie masz konta?",
        haveAccount: "Masz już konto?",

        // Dashboard
        dashboard: "Tablica",
        points: "Punkty",
        streak: "Seria",
        badges: "Odznaki",
        startSession: "Rozpocznij nową sesję",
        exerciseType: "Typ ćwiczenia",
        difficulty: "Poziom trudności",
        numExercises: "Liczba ćwiczeń",
        start: "Rozpocznij",
        scheduledSessions: "Zaplanowane sesje",
        addSchedule: "Dodaj harmonogram",
        noScheduled: "Brak zaplanowanych sesji",
        recentSessions: "Ostatnie sesje",
        noSessions: "Brak sesji",

        // Exercise Types
        wordNaming: "Nazywanie słów",
        sentenceCompletion: "Uzupełnianie zdań",
        imageRecognition: "Rozpoznawanie obrazów",
        pronunciation: "Wymowa",

        // Difficulty Levels
        easy: "Łatwy",
        medium: "Średni",
        hard: "Trudny",

        // Exercise Page
        exit: "Wyjdź",
        submit: "Zatwierdź",
        record: "Nagraj",
        correct: "Poprawnie! Świetna robota!",
        incorrect: "Nie tym razem.",
        correctAnswer: "Prawidłowa odpowiedź",
        hint: "Podpowiedź",
        chooseWords: "Wybierz z listy",
        useTiles: "Ułóż z liter",
        undo: "Cofnij",
        space: "spacja",
        nextExercise: "Dalej",
        playRecording: "▶ Odsłuchaj nagranie",
        howDidItGo: "Jak poszło?",
        rateSaid: "Udało się",
        rateNotYet: "Jeszcze nie",
        rateFirst: "Najpierw wybierz, jak poszło.",
        heard: "Przeglądarka usłyszała:",
        keepPractising: "Nic nie szkodzi. Ćwicz dalej, będzie coraz łatwiej.",
        tryAgainPractice: "Spróbuj jeszcze raz",
        practiceRight: "Tak jest.",
        practiceWrong: "Jeszcze nie. Odpowiedź to:",
        almostRight: "Prawie. Odpowiedź to:",
        largerText: "Większy tekst",
        readAloud: "Przeczytaj",

        // Messages in the app (U12)
        ok: "OK",
        tryAgain: "Coś poszło nie tak. Spróbuj ponownie za chwilę.",
        loginFailed: "Nazwa użytkownika lub hasło są nieprawidłowe.",
        accountInactive: "To konto jest wyłączone. Zapytaj logopedę lub administratora.",
        accountTaken: "Ta nazwa użytkownika lub ten e-mail są już zajęte. Wybierz inne albo się zaloguj.",
        signUpCheck: "Sprawdź formularz: hasło musi mieć co najmniej 8 znaków, a adres e-mail musi być pełny.",
        exportFailed: "Nie udało się przygotować pliku. Spróbuj ponownie.",
        scheduleFailed: "Nie udało się zapisać planu. Sprawdź datę i spróbuj ponownie.",
        startFailed: "Nie udało się rozpocząć sesji. Spróbuj ponownie.",
        answerFirst: "Najpierw wybierz lub wpisz odpowiedź.",
        answerFailed: "Nie udało się wysłać odpowiedzi. Sprawdź połączenie i spróbuj ponownie.",
        sessionDone: "Sesja zakończona. Twój wynik: {score}%.",
        deletePlanFailed: "Nie udało się usunąć planu. Spróbuj ponownie.",
        userStatusFailed: "Nie udało się zmienić konta. Spróbuj ponownie.",
        microphoneBlocked: "Mikrofon jest zablokowany. Zezwól na niego w ustawieniach przeglądarki i spróbuj ponownie.",
        leaveTitle: "Wyjść z tej sesji?",
        leaveText: "Sesja pozostanie niedokończona i nie będzie wliczana do wyników.",
        stay: "Zostań",
        leave: "Wyjdź",
        seeResult: "Zobacz wynik",
        hintsUsed: "Użyte podpowiedzi",

        // Progress
        myProgress: "Mój postęp",
        progress: "Postęp",
        exportCSV: "Eksportuj CSV",
        exportPDF: "Eksportuj PDF",
        totalSessions: "Wszystkie sesje",
        avgAccuracy: "Średnia dokładność",
        totalTime: "Całkowity czas",
        longestStreak: "Najdłuższa seria",
        progressChart: "Postęp w czasie",
        earnedBadges: "Zdobyte odznaki",
        noBadges: "Brak odznak",

        // Admin
        admin: "Administrator",
        adminDashboard: "Panel administratora",
        totalUsers: "Wszyscy użytkownicy",
        activeUsers: "Aktywni użytkownicy",
        platformAccuracy: "Dokładność platformy",
        allUsers: "Wszyscy użytkownicy",

        // Modal
        scheduleSession: "Zaplanuj sesję",
        title: "Tytuł",
        dateTime: "Data i godzina",
        cancel: "Anuluj",
        schedule: "Zaplanuj",

        // Account
        account: "Konto",
        changePassword: "Zmień hasło",
        currentPassword: "Obecne hasło",
        newPassword: "Nowe hasło (co najmniej 8 znaków)",
        passwordChanged: "Hasło zostało zmienione. Na innych urządzeniach nastąpiło wylogowanie.",
        wrongCurrentPassword: "Obecne hasło jest nieprawidłowe.",
        newPasswordRules: "Nowe hasło musi mieć co najmniej 8 znaków.",
        tooManyAttempts: "Zbyt wiele błędnych haseł. Odczekaj do 15 minut i spróbuj ponownie.",
        yourChoices: "Twoje zgody",
        consentRecordingsLabel: "Przechowuj moje nagrania głosu",
        consentSpeechLabel: "Używaj rozpoznawania mowy przeglądarki",
        saved: "Zapisano.",

        // Consent questions
        recordingsConsentTitle: "Przechowywać Twoje nagrania?",
        recordingsConsentText: "Aby ćwiczyć mówienie, aplikacja nagrywa Twój głos. Czy możemy przechowywać nagrania na serwerze? Odtworzyć je możesz tylko Ty. Możesz to zmienić w każdej chwili na stronie Konto.",
        recordingsConsentYes: "Tak, przechowuj",
        speech_recognitionConsentTitle: "Używać rozpoznawania mowy?",
        speech_recognitionConsentText: "Przeglądarka może spróbować rozpoznać, co mówisz. W tym celu może wysłać Twój głos do firmy, która ją stworzyła. Mowę osób z afazją często rozpoznaje błędnie. Możesz to zmienić w każdej chwili na stronie Konto.",
        speech_recognitionConsentYes: "Tak, używaj",
        consentNo: "Nie",
        recordingOff: "Nagrywanie jest wyłączone. Możesz je włączyć na stronie Konto.",

        // Your data
        privacyNotice: "Informacja o prywatności",
        yourData: "Twoje dane",
        yourDataText: "Pobierz wszystko, co aplikacja o Tobie przechowuje, albo usuń swoje konto.",
        downloadData: "Pobierz moje dane",
        deleteAccount: "Usuń moje konto",
        deleteTitle: "Usunąć Twoje konto?",
        deleteText: "To usunie Twoje konto, odpowiedzi, wyniki i nagrania. Nie da się tego cofnąć. Wpisz hasło, aby potwierdzić.",
        deleteForGood: "Usuń na zawsze",
        passwordNotRight: "Hasło jest nieprawidłowe.",

        // Common
        save: "Zapisz",
        delete: "Usuń",
        edit: "Edytuj",
        close: "Zamknij",
        loading: "Ładowanie...",
        error: "Wystąpił błąd",
        success: "Sukces",
    }
};

class I18n {
    constructor() {
        this.currentLang = localStorage.getItem('language') || 'en';
    }

    setLanguage(lang) {
        if (translations[lang]) {
            this.currentLang = lang;
            localStorage.setItem('language', lang);
            this.updatePageTranslations();
            return true;
        }
        return false;
    }

    translate(key) {
        return translations[this.currentLang][key] || key;
    }

    updatePageTranslations() {
        // Screen readers and the browser's own tools use this to pick the
        // pronunciation and spelling rules.
        document.documentElement.lang = this.currentLang;

        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.translate(key);

            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = translation;
            } else if (element.tagName === 'OPTION') {
                element.textContent = translation;
            } else {
                element.textContent = translation;
            }
        });

        // The privacy notice opens at the current language's section.
        document.querySelectorAll('.privacy-link').forEach((link) => {
            link.href = `privacy.html#${this.currentLang}`;
        });

        // Accessible names of buttons that show only a symbol.
        document.querySelectorAll('[data-i18n-label]').forEach((element) => {
            element.setAttribute('aria-label', this.translate(element.getAttribute('data-i18n-label')));
        });

        // Update language toggle button
        const langText = document.getElementById('lang-text');
        if (langText) {
            langText.textContent = this.currentLang.toUpperCase();
        }
    }

    getCurrentLanguage() {
        return this.currentLang;
    }
}

// Create global i18n instance
const i18n = new I18n();
