# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application files
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt 

# Install Nginx
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Copy custom Nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Expose ports
EXPOSE 80


# Start Nginx and the application
CMD service nginx start && hypercorn app:app --bind 0.0.0.0:8080 --log-level debug --keep-alive 300
