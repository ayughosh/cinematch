# Use official lightweight Python image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy your entire project to /app (including run.py and app folder)
COPY . .

# Install system dependencies (optional but safe for psycopg2 and others)
RUN apt-get update && \
    apt-get install -y curl gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask (Gunicorn) will listen on inside container
EXPOSE 5000

# Start your Flask app using Gunicorn in production mode
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]

