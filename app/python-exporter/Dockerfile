# Use official Python slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Prevent Python from creating .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app  

# Copy only requirements first (this layer will be cached if requirements.txt doesn't change)
COPY requirements.txt .

# Install dependencies (this layer will be cached)
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
