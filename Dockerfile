FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY ai_code_reviewer.py .
COPY multi_provider_integration.py .
COPY config_manager.py .
COPY code-review-config.txt .

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Default to current directory if no path provided\n\
REPO_PATH=${REPO_PATH:-/workspace}\n\
cd $REPO_PATH\n\
\n\
# Run AI code reviewer with provided arguments\n\
python /app/ai_code_reviewer.py "$@"' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create workspace directory
RUN mkdir -p /workspace
WORKDIR /workspace

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python /app/ai_code_reviewer.py --help > /dev/null || exit 1

# Use entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

# Default command shows help
CMD ["--help"]

# Labels for metadata
LABEL maintainer="your.email@example.com"
LABEL description="AI-powered code review tool with multi-provider support"
LABEL version="1.0.0"