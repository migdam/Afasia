# Included in every nginx location (see nginx.conf): a location with its own
# add_header drops the server-level ones.
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
