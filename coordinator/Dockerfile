# Use the official Python 3.10 image as the base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements to avoid rebuilding unnecessary layers
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . ./

