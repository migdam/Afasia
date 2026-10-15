/**
 * UI Module
 * Handles user interface updates and interactions
 */

class UIManager {
    constructor() {
        this.currentPage = 'auth';
        this.currentUser = null;
    }

    showPage(pageName) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });

        // Show selected page
        const page = document.getElementById(`${pageName}-page`);
        if (page) {
            page.classList.add('active');
            this.currentPage = pageName;
        }

        // Update bottom nav
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('data-page') === pageName) {
                item.classList.add('active');
            }
        });
    }

    showAuthPage() {
        // Start again from an empty login form, so nothing typed earlier (a
        // password included) is left on screen for the next person.
        document.getElementById('login-form-submit').reset();
        document.getElementById('register-form-submit').reset();
        document.getElementById('register-form').style.display = 'none';
        document.getElementById('login-form').style.display = 'block';
        this.showPage('auth');
        document.querySelector('.bottom-nav').style.display = 'none';
        document.getElementById('logout-btn').style.display = 'none';
    }

    showDashboard(user) {
        this.currentUser = user;
        this.showPage('dashboard');
        document.querySelector('.bottom-nav').style.display = 'flex';
        document.getElementById('logout-btn').style.display = 'block';

        // Admin nav for admins and therapists only; hidden again for anyone
        // else who logs in on the same page.
        const isStaff = user.role === 'admin' || user.role === 'therapist';
        document.getElementById('admin-nav').style.display = isStaff ? 'flex' : 'none';

        this.updateUserStats(user);
        this.loadBadgeCount();
    }

    async loadBadgeCount() {
        try {
            const badges = await api.getBadges();
            document.getElementById('badge-count').textContent = badges.length;
        } catch (error) {
            console.error('Failed to load badges:', error);
        }
    }

    updateUserStats(user) {
        document.getElementById('total-points').textContent = user.total_points || 0;
        document.getElementById('current-streak').textContent = user.current_streak || 0;
    }

    async loadRecentSessions() {
        try {
            const sessions = await api.getSessions(0, 5);
            const container = document.getElementById('recent-sessions');

            if (sessions.length === 0) {
                container.innerHTML = `<p class="empty-state" data-i18n="noSessions">${i18n.translate('noSessions')}</p>`;
                return;
            }

            container.innerHTML = sessions.map(session => this.renderSessionItem(session)).join('');
            i18n.updatePageTranslations();
        } catch (error) {
            console.error('Failed to load sessions:', error);
        }
    }

    async loadScheduledSessions() {
        try {
            const sessions = await api.getScheduledSessions();
            const container = document.getElementById('scheduled-list');

            if (sessions.length === 0) {
                container.innerHTML = `<p class="empty-state" data-i18n="noScheduled">${i18n.translate('noScheduled')}</p>`;
                return;
            }

            container.innerHTML = sessions.map(session => this.renderScheduledItem(session)).join('');
            i18n.updatePageTranslations();
        } catch (error) {
            console.error('Failed to load scheduled sessions:', error);
        }
    }

    renderSessionItem(session) {
        const date = new Date(session.started_at).toLocaleDateString();
        const difficultyClass = `badge-${session.difficulty}`;
        const statusClass = session.is_completed ? 'badge-completed' : '';

        return `
            <div class="session-item">
                <div class="session-header">
                    <div>
                        <div class="session-title">${session.title}</div>
                        <div class="session-meta">
                            <span>${date}</span>
                            <span class="badge ${difficultyClass}">${session.difficulty}</span>
                            ${session.is_completed ? `<span class="badge ${statusClass}">Completed</span>` : ''}
                        </div>
                    </div>
                    ${session.is_completed ? `<div class="session-score">${Math.round(session.score)}%</div>` : ''}
                </div>
            </div>
        `;
    }

    renderScheduledItem(session) {
        const dateTime = new Date(session.scheduled_time).toLocaleString();
        const difficultyClass = `badge-${session.difficulty}`;

        return `
            <div class="session-item">
                <div class="session-header">
                    <div>
                        <div class="session-title">${session.title}</div>
                        <div class="session-meta">
                            <span>📅 ${dateTime}</span>
                            <span class="badge ${difficultyClass}">${session.difficulty}</span>
                        </div>
                    </div>
                    <button class="btn btn-sm btn-secondary" onclick="ui.deleteSchedule(${session.id})">
                        ${i18n.translate('delete')}
                    </button>
                </div>
            </div>
        `;
    }

    async deleteSchedule(sessionId) {
        try {
            await api.deleteScheduledSession(sessionId);
            await this.loadScheduledSessions();
        } catch (error) {
            alert('Failed to delete scheduled session');
        }
    }

    async loadProgress() {
        try {
            const progress = await api.getProgress(30);
            const badges = await api.getBadges();

            // Update stats
            document.getElementById('progress-total-sessions').textContent = progress.total_sessions;
            document.getElementById('progress-avg-accuracy').textContent = `${progress.average_accuracy}%`;
            document.getElementById('progress-total-time').textContent = `${progress.total_time_hours}h`;
            document.getElementById('progress-longest-streak').textContent = progress.longest_streak;
            document.getElementById('badge-count').textContent = badges.length;

            // Draw chart
            const chart = new SimpleChart('progress-chart');
            if (progress.progress_history && progress.progress_history.length > 0) {
                const labels = progress.progress_history.reverse().map(p =>
                    new Date(p.date).toLocaleDateString()
                );
                const data = progress.progress_history.map(p => p.accuracy_rate);

                chart.drawLineChart(labels, [{
                    label: 'Accuracy %',
                    data: data,
                    color: '#4F46E5'
                }]);
            }

            // Load badges
            this.loadBadges(badges);
        } catch (error) {
            console.error('Failed to load progress:', error);
        }
    }

    loadBadges(badges) {
        const container = document.getElementById('badges-container');

        if (badges.length === 0) {
            container.innerHTML = `<p class="empty-state" data-i18n="noBadges">${i18n.translate('noBadges')}</p>`;
            return;
        }

        const badgeIcons = {
            first_session: '🎯',
            week_streak: '🔥',
            month_streak: '🏆',
            perfectionist: '💎',
            dedicated: '⭐',
            master: '👑',
        };

        container.innerHTML = badges.map(badge => `
            <div class="badge-item">
                <div class="badge-icon">${badgeIcons[badge.badge_type] || '🏅'}</div>
                <div class="badge-name">${badge.badge_type.replace('_', ' ')}</div>
                <div class="badge-date">${new Date(badge.earned_at).toLocaleDateString()}</div>
            </div>
        `).join('');
    }

    async loadAdminDashboard() {
        try {
            const stats = await api.getAdminStats();
            const users = await api.getAllUsers();

            // Update stats
            document.getElementById('admin-total-users').textContent = stats.total_users;
            document.getElementById('admin-active-users').textContent = stats.active_users;
            document.getElementById('admin-total-sessions').textContent = stats.total_sessions;
            document.getElementById('admin-avg-accuracy').textContent = `${stats.average_accuracy}%`;

            // Load users
            const container = document.getElementById('admin-users-list');
            container.replaceChildren(...users.map(user => this.renderAdminUser(user)));
        } catch (error) {
            console.error('Failed to load admin dashboard:', error);
        }
    }

    renderAdminUser(user) {
        // Built with DOM methods: usernames and emails are whatever people
        // typed, so they must never be parsed as HTML.
        const item = document.createElement('div');
        item.className = 'user-item';

        const info = document.createElement('div');
        info.className = 'user-info';
        const name = document.createElement('h4');
        name.textContent = user.username;
        const details = document.createElement('p');
        details.textContent = `${user.email} • Points: ${user.total_points}`;
        info.append(name, details);

        const actions = document.createElement('div');
        actions.className = 'user-actions';
        const toggle = document.createElement('button');
        toggle.className = `btn btn-sm ${user.is_active ? 'btn-secondary' : 'btn-primary'}`;
        toggle.textContent = user.is_active ? 'Deactivate' : 'Activate';
        toggle.addEventListener('click', () => this.toggleUserStatus(user.id, user.is_active));
        actions.append(toggle);

        item.append(info, actions);
        return item;
    }

    async toggleUserStatus(userId, isActive) {
        try {
            if (isActive) {
                await api.deactivateUser(userId);
            } else {
                await api.activateUser(userId);
            }
            await this.loadAdminDashboard();
        } catch (error) {
            alert('Failed to update user status');
        }
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
        }
    }

    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
        }
    }

    showNotification(message, type = 'info') {
        // Simple notification (could be enhanced with a toast library)
        alert(message);
    }

    async downloadFile(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    // Dark mode toggle (Enhancement 7)
    toggleDarkMode() {
        const body = document.body;
        const themeIcon = document.querySelector('.theme-icon');

        if (body.classList.contains('light-theme')) {
            body.classList.remove('light-theme');
            body.classList.add('dark-theme');
            themeIcon.textContent = '☀️';
            localStorage.setItem('theme', 'dark');
        } else {
            body.classList.remove('dark-theme');
            body.classList.add('light-theme');
            themeIcon.textContent = '🌙';
            localStorage.setItem('theme', 'light');
        }

        // Add animation
        themeIcon.classList.add('theme-toggle-animation');
        setTimeout(() => {
            themeIcon.classList.remove('theme-toggle-animation');
        }, 500);
    }

    loadTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        const body = document.body;
        const themeIcon = document.querySelector('.theme-icon');

        if (savedTheme === 'dark') {
            body.classList.remove('light-theme');
            body.classList.add('dark-theme');
            themeIcon.textContent = '☀️';
        } else {
            body.classList.remove('dark-theme');
            body.classList.add('light-theme');
            themeIcon.textContent = '🌙';
        }
    }
}

// Create global UI manager instance
const ui = new UIManager();
