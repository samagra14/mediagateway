FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create storage directories
RUN mkdir -p /app/storage/videos /app/storage/temp

# Expose port
EXPOSE 3001

# Run application
CMD ["python", "run.py"]
