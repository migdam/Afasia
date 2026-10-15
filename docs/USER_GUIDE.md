# User guide

[🇵🇱 Przewodnik po polsku](USER_GUIDE.pl.md)

This guide describes the app as it is today: an early version for trying out, not for clinical use (see the [README](../README.md)). It is meant to support work with a speech-language therapist, not to replace it.

## Before you start

- **Browser:** a recent Chrome, Edge, Firefox or Safari, on a computer, tablet or phone. The app is tested in Chrome.
- **Address:** whoever runs the app gives you its address, for example `http://localhost:3000`.
- **Microphone:** only needed for pronunciation exercises, which don't work reliably yet (see [Pronunciation](#pronunciation)).

## Language and theme

The buttons at the top right of every screen:
- **EN / PL** switches the language between English and Polish.
- **🌙 / ☀️** switches between the light and dark theme.

Your browser remembers both choices.

The exercises come in the language you choose. A few messages also still appear in English when Polish is chosen: pop-up messages, "Completed" in the session list, and the admin buttons.

## Your account

**To sign up:**
1. Click **Register** under the login form.
2. Fill in your email, a username, your full name (optional) and a password of at least 8 characters.
3. Click **Register**. You go straight to your dashboard.

**To log in:** type your username and password and click **Login**.

**To log out:** click **Logout** at the top right. The login form is emptied, so the next person can't see what you typed.

While you use the app, you stay logged in. After 30 minutes without using it, or 12 hours after you logged in, you have to log in again. There is no "forgot password" yet.

**To change your password:** tap **Account** at the bottom of the screen. Type your current password and a new one of at least 8 characters, then click **Change password**. A message under the button says whether it worked. You stay logged in here, but on your other devices you have to log in again with the new password.

## The dashboard

At the top are three numbers:
- **Points:** see [Points, streaks and badges](#points-streaks-and-badges).
- **Streak:** how many days in a row you finished a session.
- **Badges:** how many badges you have earned.

Below them:
- **Start New Session:** begin practising.
- **Scheduled Sessions:** sessions you planned for later.
- **Recent Sessions:** your last five sessions, with their scores.

The bar at the bottom switches between **Dashboard** and **Progress**. Therapists and admins also see **Admin**.

## Practising

1. Under **Start New Session**, choose:
   - **Exercise Type:** Word Naming, Sentence Completion or Pronunciation.
   - **Difficulty:** Easy, Medium or Hard.
   - **Number of Exercises:** 5 to 50. Short sessions of 5 to 10 are a good start.
2. Click **Start**.
3. Answer the exercise, then click **Submit**.
4. You'll see either **"Correct! Well done!"** or **"Not quite. Correct answer: …"**, with the right answer in bold.
5. After 2 seconds the next exercise appears by itself.

At the top of the exercise screen:
- **Exit** leaves the session. You're asked to confirm. A session you leave stays unfinished and doesn't count towards your scores.
- The counter and bar show how far you are, for example **3/10**.
- The clock shows how long the session has taken. There is no time limit.

After the last exercise, a message shows your score, for example "Session complete! Score: 80%", and you return to the dashboard.

### Word Naming

You read a short description of an everyday thing, such as "A pet that barks and wags its tail". Type its name (**dog**) in the box and click **Submit**.

The answer must match exactly, apart from capital letters and spaces at the ends; some words have accepted alternatives, such as **bike** for **bicycle**. There are no pictures yet.

**If the word doesn't come**, click **Hint**. Each click gives a little more help: first what the thing is for and where you find it, then its first letter, then the word itself. A right answer after hints earns fewer points, and the message says how many hints you used.

### Sentence Completion

You read a sentence with a gap, such as "The sky is ___". Click the word that fits, then **Submit**. If you click **Submit** without choosing, the app asks you to choose an answer first.

### Pronunciation

You see a word or phrase to say, such as "Say: Hello". Click **Record**, say it, click the button again to stop, then click **Submit**. The first time, the app asks whether it may keep your recordings (see [Your data](#your-data)), and your browser asks for permission to use the microphone. The microphone is on only while you record: it turns off when you stop, leave the session or log out, and your browser stops showing it as in use.

**This doesn't work reliably yet.** Your answer is judged by the browser's own speech recognition. In most browsers that isn't available, and where it is, it's unreliable for speech affected by aphasia. Answers are often marked wrong when they were right. This exercise type is being redesigned.

### Image Recognition

Not available yet: there are no exercises of this type, so the app doesn't offer it.

## Points, streaks and badges

- **Points:** every correct answer earns 10 points on Easy, 20 on Medium and 30 on Hard. They're added when you finish the session.
- **Streak:** finishing a session on consecutive days builds a streak. Days are counted in UTC, so just after midnight in Poland may still count as the day before.
- **Badges:** you earn one for your first finished session, for a 7-day streak and for a 30-day streak.

## Your progress

Click **Progress** in the bottom bar. You'll see:
- **Total Sessions:** finished sessions.
- **Average Accuracy:** the share of all your answers that were right.
- **Total Time:** the time from the start of each finished session to its last answer, in hours.
- **Longest Streak.**
- **Progress Over Time:** a chart of each session's score over the last 30 days.
- **Earned Badges.**

**Export CSV** downloads every finished session as a spreadsheet file. **Export PDF** downloads a short report with your totals and your last 10 sessions. You can give either one to your therapist.

## Planning sessions

Click **Add Schedule** on the dashboard. Give the session a title, a date and time, a type and a difficulty, then click **Schedule**. Upcoming sessions are listed on the dashboard, and **Delete** removes one.

The app doesn't remind you of planned sessions yet, and starting one is up to you: use **Start New Session**.

## For therapists and admins

**Admin** in the bottom bar shows:
- the number of patients, active patients and finished sessions, and the share of right answers across everyone;
- every patient, with their email and points;
- a **Deactivate** button for each active patient: a deactivated patient can't log in until you click **Activate**.

At the moment every therapist sees every patient. Signing up always makes a patient account; therapist and admin accounts are made by whoever runs the server (see the README).

## Your data

Everything you do is stored on the server that runs the app: your account, your answers and your scores. Recordings are kept only if you agree. The first time you click **Record**, the app asks whether it may keep your recordings; if you say no, the microphone stays off. Before using your browser's speech recognition, which may send your voice to the company that made the browser, it asks separately. You can change both answers at any time under **Your choices** on the **Account** page. Under **Your data** on the **Account** page you can:

- **Download my data:** saves everything the app keeps about you as one file (JSON).
- **Delete my account:** after you type your password, deletes your account, answers, scores and recordings. This can't be undone.

The **Privacy notice** link, on the login page and the Account page, explains what the app keeps, why, and who can see it.

## When something goes wrong

| What happens | What to do |
|---|---|
| "Incorrect username or password" | Check the spelling and Caps Lock. Usernames are case-sensitive. |
| "Inactive user" | Your account was deactivated. Ask your therapist or admin. |
| "Too many failed attempts" | After 5 wrong passwords, logging in to that account from your device is paused for up to 15 minutes. Wait, then try again. |
| You're back at the login page | Your login ended after 30 minutes without use, or 12 hours after you logged in. Log in again. |
| "Failed to start session" | The server may be down. Try again later, or tell whoever runs the app. |
| "Please provide an answer" | Type a word or choose an option before **Submit**. |
| The microphone doesn't work | Allow it in your browser's site settings and reload. Pronunciation is unreliable anyway (see above). |

## Questions

Ask whoever runs the app for you, or open an issue in the project's repository.
