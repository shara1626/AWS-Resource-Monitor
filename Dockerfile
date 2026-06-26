# We start with an official Python image
# It has Python pre-installed so we don't set it up manually
# slim = smaller file size, faster to download on AWS
FROM python:3.11-slim

# We set /app as our working directory
# All files go here inside the container
# Like cd /app - every command runs from here
WORKDIR /app

# We copy requirements.txt FIRST (before app code)
# Docker caches each step - if requirements don't change
# Docker skips reinstalling them on next build
# This makes rebuilds much faster
COPY requirements.txt .

# Copy our main Python server file
COPY app.py .

# Copy the frontend HTML/CSS files
# Flask needs these to serve to the browser
COPY templates/ ./templates

# Copy environment variables

# Install all Python libraries
# Runs inside the container during build
# Like "npm install" in Node.js
RUN pip install --no-cache-dir -r requirements.txt

# Tell Docker our app uses port 3000
# This is documentation + allows port mapping
# When running on AWS we map this to port 80
EXPOSE 3000

# This is the command that starts our app
# Runs automatically when container starts
# Like "npm run start" in Node.js
CMD ["python", "app.py"]
