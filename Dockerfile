# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt 

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application using Hypercorn with timeout set to 300 seconds
# CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:8080", "--log-level", "debug", "--timeout", "300"]
CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:8080", "--log-level", "debug"]
