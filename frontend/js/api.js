/**
 * API Client Module
 * Handles all API communication with the backend
 */

// Set by js/config.js.
const API_BASE_URL = window.API_BASE_URL;

class APIClient {
    constructor() {
        // The login lives in an httpOnly cookie that scripts can't read.
        // Versions before P1-5c2 kept it here; don't leave it lying around.
        localStorage.removeItem('access_token');
        // When the current token was issued and when it ends (Unix seconds),
        // from the last login or renewal; unknown after a page load.
        this.tokenTimes = null;
        this.renewal = null;
        this.renewRefused = false;
    }

    noteLogin(data) {
        this.tokenTimes = { issued: data.issued_at, expires: data.expires_at };
        this.renewRefused = false;
    }

    // Every call sends the login cookie, and the X-Requested-With header the
    // server asks for before it accepts a change made through the cookie.
    fetch(endpoint, options = {}) {
        return fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            credentials: 'include',
            headers: { 'X-Requested-With': 'afasia', ...options.headers },
        });
    }

    // A login runs out after a stretch of not using the app. While the app
    // is in use, renew it once half its life is gone (or straight away after
    // a page load, when its age is unknown). The server stops renewing a login
    // some hours after it began; then it simply runs out.
    renewIfStale() {
        if (this.renewal || this.renewRefused) {
            return;
        }
        const times = this.tokenTimes;
        if (times && Date.now() / 1000 - times.issued < (times.expires - times.issued) / 2) {
            return;
        }
        this.renewal = this.request('/auth/refresh', { method: 'POST' })
            .then((data) => this.noteLogin(data))
            .catch(() => { this.renewRefused = true; })
            .finally(() => { this.renewal = null; });
    }

    async request(endpoint, options = {}) {
        try {
            const response = await this.fetch(endpoint, {
                ...options,
                headers: { 'Content-Type': 'application/json', ...options.headers },
            });

            const data = await response.json().catch(() => null);

            if (!response.ok) {
                throw new Error(data?.detail || 'Request failed');
            }

            if (!endpoint.startsWith('/auth/')) {
                this.renewIfStale();
            }
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Auth endpoints
    async register(userData) {
        const data = await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
        this.noteLogin(data);
        return data;
    }

    async login(credentials) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials),
        });
        this.noteLogin(data);
        return data;
    }

    async logout() {
        // A renewal still under way would set the cookie again afterwards.
        await this.renewal;
        this.tokenTimes = null;
        await this.request('/auth/logout', { method: 'POST' }).catch(() => {});
    }

    // User endpoints
    async getProfile() {
        return this.request('/users/profile');
    }

    async updateProfile(updates) {
        return this.request('/users/profile', {
            method: 'PUT',
            body: JSON.stringify(updates),
        });
    }

    async getProgress(days = 30) {
        return this.request(`/users/progress?days=${days}`);
    }

    async getBadges() {
        return this.request('/users/badges');
    }

    async getScheduledSessions() {
        return this.request('/users/scheduled-sessions');
    }

    async createScheduledSession(sessionData) {
        return this.request('/users/scheduled-sessions', {
            method: 'POST',
            body: JSON.stringify(sessionData),
        });
    }

    async deleteScheduledSession(sessionId) {
        return this.request(`/users/scheduled-sessions/${sessionId}`, {
            method: 'DELETE',
        });
    }

    async exportProgressCSV() {
        const response = await this.fetch(`/users/progress/export/csv`);
        const blob = await response.blob();
        return blob;
    }

    async exportProgressPDF() {
        const response = await this.fetch(`/users/progress/export/pdf`);
        const blob = await response.blob();
        return blob;
    }

    async uploadAudio(exerciseId, audioBlob) {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording');

        const response = await this.fetch(`/users/audio/upload?exercise_id=${exerciseId}`, {
            method: 'POST',
            body: formData,
        });

        return response.json();
    }

    // Therapy endpoints
    async createSession(sessionData) {
        return this.request('/therapy/sessions', {
            method: 'POST',
            body: JSON.stringify(sessionData),
        });
    }

    async getSessions(skip = 0, limit = 20) {
        return this.request(`/therapy/sessions?skip=${skip}&limit=${limit}`);
    }

    async getSession(sessionId) {
        return this.request(`/therapy/sessions/${sessionId}`);
    }

    async getExercises(sessionId) {
        return this.request(`/therapy/sessions/${sessionId}/exercises`);
    }

    async submitAnswer(exerciseId, answer, timeTaken) {
        return this.request(`/therapy/exercises/${exerciseId}/answer`, {
            method: 'POST',
            body: JSON.stringify({
                answer: answer,
                time_taken_seconds: timeTaken,
            }),
        });
    }

    async completeSession(sessionId) {
        return this.request(`/therapy/sessions/${sessionId}/complete`, {
            method: 'POST',
        });
    }

    // Admin endpoints
    async getAdminStats() {
        return this.request('/admin/stats');
    }

    async getAllUsers(skip = 0, limit = 50) {
        return this.request(`/admin/users?skip=${skip}&limit=${limit}`);
    }

    async getUserSessions(userId, skip = 0, limit = 20) {
        return this.request(`/admin/users/${userId}/sessions?skip=${skip}&limit=${limit}`);
    }

    async activateUser(userId) {
        return this.request(`/admin/users/${userId}/activate`, {
            method: 'PUT',
        });
    }

    async deactivateUser(userId) {
        return this.request(`/admin/users/${userId}/deactivate`, {
            method: 'PUT',
        });
    }
}

// Create global API client instance
const api = new APIClient();
