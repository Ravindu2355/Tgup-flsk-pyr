# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install ffmpeg
#RUN apt-get update && apt-get install -y ffmpeg && apt-get clean
#RUN apt -qq update && apt -qq install -y git python3 python3-pip ffmpeg

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose the port the app runs on (not strictly necessary for a Telegram bot)
#EXPOSE 8000

# Run the bot when the container launches
CMD python3 bot.py