/**
 * API Client Module
 * Handles all API communication with the backend
 */

// Set by js/config.js.
const API_BASE_URL = window.API_BASE_URL;

class APIClient {
    constructor() {
        this.token = localStorage.getItem('access_token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('access_token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('access_token');
    }

    async request(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                ...options,
                headers,
            });

            const data = await response.json().catch(() => null);

            if (!response.ok) {
                throw new Error(data?.detail || 'Request failed');
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
        this.setToken(data.access_token);
        return data;
    }

    async login(credentials) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials),
        });
        this.setToken(data.access_token);
        return data;
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
        const response = await fetch(`${API_BASE_URL}/users/progress/export/csv`, {
            headers: {
                'Authorization': `Bearer ${this.token}`,
            },
        });
        const blob = await response.blob();
        return blob;
    }

    async exportProgressPDF() {
        const response = await fetch(`${API_BASE_URL}/users/progress/export/pdf`, {
            headers: {
                'Authorization': `Bearer ${this.token}`,
            },
        });
        const blob = await response.blob();
        return blob;
    }

    async uploadAudio(exerciseId, audioBlob) {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording');

        const response = await fetch(`${API_BASE_URL}/users/audio/upload?exercise_id=${exerciseId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
            },
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
