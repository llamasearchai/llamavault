FROM python:3.10-slim

WORKDIR /app

# Install dependencies first to leverage Docker cache
COPY pyproject.toml .
RUN pip install --no-cache-dir .[web]

# Copy the source code
COPY . .

# Create volume for vault data
VOLUME /data

# Set environment variables
ENV LLAMAVAULT_DIR=/data

# Expose port for web interface
EXPOSE 5000

# Run web interface by default
CMD ["llamavault", "web", "--host", "0.0.0.0"] 