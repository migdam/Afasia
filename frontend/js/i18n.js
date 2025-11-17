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
        incorrect: "Incorrect. Try again!",

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
        incorrect: "Niepoprawnie. Spróbuj ponownie!",

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
