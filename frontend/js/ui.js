/**
 * UI Module
 * Handles user interface updates and interactions
 */

/**
 * Make an element. Text always goes in as textContent, never as HTML, so
 * whatever people typed (titles, names) can't become page markup.
 */
function el(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
}

/** Show a translated "nothing here yet" message in a list. */
function showEmpty(container, key) {
    const message = el('p', 'empty-state', i18n.translate(key));
    message.dataset.i18n = key;
    container.replaceChildren(message);
}

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
            // Start keyboard and screen-reader users at the new page's heading.
            this.focusHeading(page.querySelector('h2'));
        }

        // Update bottom nav
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('data-page') === pageName) {
                item.classList.add('active');
            }
        });
    }

    // A message under a form, in words, in the current language. Errors are
    // announced at once (role="alert"); other news politely (role="status").
    showFormMessage(id, key, kind) {
        const message = document.getElementById(id);
        message.className = `form-message ${kind}`;
        message.setAttribute('role', kind === 'error' ? 'alert' : 'status');
        message.setAttribute('data-i18n', key);  // re-translated if the language changes
        message.textContent = i18n.translate(key);
        this.updateReadAloud();
    }

    // Ask a consent question in an in-app dialog. Resolves to true (yes),
    // false (no) or null (closed with Escape: no answer).
    askConsent(kind) {
        const dialog = document.getElementById('consent-dialog');
        document.getElementById('consent-title').textContent = i18n.translate(`${kind}ConsentTitle`);
        document.getElementById('consent-text').textContent = i18n.translate(`${kind}ConsentText`);
        this.updateReadAloud();
        const yes = document.getElementById('consent-yes');
        const no = document.getElementById('consent-no');
        yes.textContent = i18n.translate(`${kind}ConsentYes`);
        no.textContent = i18n.translate('consentNo');
        return new Promise((resolve) => {
            const finish = (answer) => {
                yes.onclick = no.onclick = dialog.oncancel = null;
                if (dialog.open) dialog.close();
                resolve(answer);
            };
            yes.onclick = () => finish(true);
            no.onclick = () => finish(false);
            dialog.oncancel = (event) => { event.preventDefault(); finish(null); };
            dialog.showModal();
            no.focus();  // the choice that does nothing is the safe default
        });
    }

    // A "Read aloud" button for whatever getText returns (U3).
    readAloudButton(getText, id = null, target = null) {
        const button = el('button', 'btn btn-secondary read-aloud');
        button.type = 'button';
        if (id) button.id = id;
        const label = el('span', '', i18n.translate('readAloud'));
        label.dataset.i18n = 'readAloud';
        button.append(el('span', '', '🔊 '), label);
        button.firstChild.setAttribute('aria-hidden', 'true');
        button.addEventListener('click', () => reader.read(getText(), i18n.getCurrentLanguage()));
        button.readTarget = target;  // hidden while this element has no text
        button.hidden = !reader.canRead(i18n.getCurrentLanguage());
        return button;
    }

    // A read-aloud button after every element marked data-read-aloud:
    // instructions, dialog texts and messages (U3).
    addReadAloudButtons() {
        document.querySelectorAll('[data-read-aloud]').forEach((target) => {
            target.after(this.readAloudButton(() => target.textContent, null, target));
        });
        this.updateReadAloud();
    }

    // Show read-aloud buttons only when there is a voice on this device for
    // the current language (it can change with the language, or once the
    // browser has loaded its voices).
    updateReadAloud() {
        const available = reader.canRead(i18n.getCurrentLanguage());
        document.querySelectorAll('.read-aloud').forEach((button) => {
            const empty = button.readTarget && !button.readTarget.textContent.trim();
            button.hidden = !available || Boolean(empty);
        });
    }

    clearFormMessage(id) {
        const message = document.getElementById(id);
        message.textContent = '';
        message.removeAttribute('data-i18n');
        message.removeAttribute('role');
        this.updateReadAloud();
    }

    // Move the focus to a heading (not a control, so it gets tabindex -1).
    focusHeading(heading) {
        if (!heading) return;
        heading.tabIndex = -1;
        heading.focus();
    }

    showAuthPage() {
        // Start again from an empty login form, so nothing typed earlier (a
        // password included) is left on screen for the next person.
        document.getElementById('login-form-submit').reset();
        document.getElementById('register-form-submit').reset();
        document.getElementById('password-form').reset();
        ['password-message', 'consent-message', 'data-message', 'login-message', 'register-message']
            .forEach((id) => this.clearFormMessage(id));
        this.clearNotice();
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
                showEmpty(container, 'noSessions');
                return;
            }

            container.replaceChildren(...sessions.map(session => this.renderSessionItem(session)));
        } catch (error) {
            console.error('Failed to load sessions:', error);
        }
    }

    async loadScheduledSessions() {
        try {
            const sessions = await api.getScheduledSessions();
            const container = document.getElementById('scheduled-list');

            if (sessions.length === 0) {
                showEmpty(container, 'noScheduled');
                return;
            }

            container.replaceChildren(...sessions.map(session => this.renderScheduledItem(session)));
        } catch (error) {
            console.error('Failed to load scheduled sessions:', error);
        }
    }

    renderSessionItem(session) {
        const meta = el('div', 'session-meta');
        meta.append(
            el('span', '', new Date(session.started_at).toLocaleDateString()),
            el('span', `badge badge-${session.difficulty}`, session.difficulty)
        );
        if (session.is_completed) {
            meta.append(el('span', 'badge badge-completed', 'Completed'));
        }

        const details = el('div');
        details.append(el('div', 'session-title', session.title), meta);
        const header = el('div', 'session-header');
        header.append(details);
        if (session.is_completed) {
            header.append(el('div', 'session-score', `${Math.round(session.score)}%`));
        }

        const item = el('div', 'session-item');
        item.append(header);
        return item;
    }

    renderScheduledItem(session) {
        const meta = el('div', 'session-meta');
        meta.append(
            el('span', '', `📅 ${new Date(session.scheduled_time).toLocaleString()}`),
            el('span', `badge badge-${session.difficulty}`, session.difficulty)
        );

        const details = el('div');
        details.append(el('div', 'session-title', session.title), meta);
        const remove = el('button', 'btn btn-sm btn-secondary', i18n.translate('delete'));
        remove.dataset.i18n = 'delete';
        remove.addEventListener('click', () => this.deleteSchedule(session.id));
        const header = el('div', 'session-header');
        header.append(details, remove);

        const item = el('div', 'session-item');
        item.append(header);
        return item;
    }

    async deleteSchedule(sessionId) {
        try {
            await api.deleteScheduledSession(sessionId);
            await this.loadScheduledSessions();
        } catch (error) {
            this.notify('deletePlanFailed');
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
            // Oldest first; with no history the chart says there's no data.
            const chart = new SimpleChart('progress-chart');
            const history = [...(progress.progress_history || [])].reverse();
            chart.drawLineChart(
                history.map(p => new Date(p.date).toLocaleDateString()),
                [{ label: 'Accuracy %', data: history.map(p => p.accuracy_rate) }]
            );

            // Load badges
            this.loadBadges(badges);
        } catch (error) {
            console.error('Failed to load progress:', error);
        }
    }

    loadBadges(badges) {
        const container = document.getElementById('badges-container');

        if (badges.length === 0) {
            showEmpty(container, 'noBadges');
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

        container.replaceChildren(...badges.map(badge => {
            const item = el('div', 'badge-item');
            item.append(
                el('div', 'badge-icon', badgeIcons[badge.badge_type] || '🏅'),
                el('div', 'badge-name', badge.badge_type.replace('_', ' ')),
                el('div', 'badge-date', new Date(badge.earned_at).toLocaleDateString())
            );
            return item;
        }));
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
            this.notify('userStatusFailed');
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

    // A message from the app at the top of the page, in the current
    // language (U12). kind: 'error' (read out at once) or 'status'.
    notify(key, kind = 'error', params = {}) {
        const box = document.getElementById('app-message-box');
        const message = document.getElementById('app-message');
        let text = i18n.translate(key);
        Object.entries(params).forEach(([name, value]) => {
            text = text.replace(`{${name}}`, value);
        });
        message.textContent = text;
        box.className = `app-message-box ${kind}`;
        box.setAttribute('role', kind === 'error' ? 'alert' : 'status');
        box.hidden = false;
        this.updateReadAloud();
    }

    clearNotice() {
        document.getElementById('app-message-box').hidden = true;
    }

    // Ask in an in-app dialog whether to leave the session; resolves to
    // true (leave) or false (stay, or the dialog closed with Escape).
    confirmLeave() {
        const dialog = document.getElementById('leave-dialog');
        const stay = document.getElementById('leave-stay');
        const go = document.getElementById('leave-go');
        return new Promise((resolve) => {
            const finish = (answer) => {
                stay.onclick = go.onclick = dialog.oncancel = null;
                if (dialog.open) dialog.close();
                resolve(answer);
            };
            stay.onclick = () => finish(false);
            go.onclick = () => finish(true);
            dialog.oncancel = (event) => { event.preventDefault(); finish(false); };
            dialog.showModal();
            stay.focus();  // staying is the safe default
        });
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
