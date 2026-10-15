FROM python:3.11-slim

WORKDIR /app

# Install dependencies. Behind a TLS-inspecting proxy, pass its CA bundle as
# the pip_ca build secret (docker-compose.yml reads it from PIP_CA_FILE); it
# is used for this step only and doesn't end up in the image.
COPY requirements.txt .
RUN --mount=type=secret,id=pip_ca \
    if [ -s /run/secrets/pip_ca ]; then export PIP_CERT=/run/secrets/pip_ca; fi; \
    pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
