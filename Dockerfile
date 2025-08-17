# Use official Python base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run with Uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]