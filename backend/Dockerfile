FROM python:3.11-slim

# Set working directory
WORKDIR /app
ENV PYTHONPATH=/app \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# No apt/gcc here. The NAS image is built as linux/amd64 on an Apple Silicon
# Mac, and apt under that emulator runs out of memory. Dependencies ship wheels.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
