// Where the API lives. The README's development setup runs it on port 8000;
// the Docker image replaces this file to use nginx's same-origin /api proxy.
// A page may set window.API_BASE_URL first (the end-to-end tests do).
window.API_BASE_URL = window.API_BASE_URL || 'http://localhost:8000/api/v1';
