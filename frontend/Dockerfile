FROM nginx:alpine

# Copy the app only (not this Dockerfile or nginx.conf, which would be served)
COPY index.html privacy.html manifest.json sw.js /usr/share/nginx/html/
COPY css /usr/share/nginx/html/css
COPY js /usr/share/nginx/html/js

# Behind nginx the API is on the same origin, under /api (see nginx.conf)
RUN echo "window.API_BASE_URL = window.API_BASE_URL || '/api/v1';" > /usr/share/nginx/html/js/config.js

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY security-headers.inc /etc/nginx/conf.d/security-headers.inc

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
