// Service worker for offline support (kept out of index.html so the
// Content-Security-Policy can forbid inline scripts).
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
        .then(() => console.log('Service Worker registered'))
        .catch(err => console.error('Service Worker registration failed:', err));
}
