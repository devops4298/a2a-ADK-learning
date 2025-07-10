# TypeScript Playwright Cucumber Code Review Agent A2A Server
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for ESLint/Prettier support (optional)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY code_review_agent/ ./code_review_agent/
COPY start_a2a_server.py .
COPY setup.py .
COPY README.md .

# Install the package
RUN pip install -e .

# Create non-root user
RUN useradd --create-home --shell /bin/bash reviewer
RUN chown -R reviewer:reviewer /app
USER reviewer

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Set environment variables
ENV ENVIRONMENT=production
ENV HOST=0.0.0.0
ENV PORT=8080
ENV PYTHONPATH=/app

# Start the A2A server
CMD ["python", "start_a2a_server.py"]
