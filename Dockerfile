# Python 3.10 base image use karo
FROM python:3.10-slim

# Working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Start bot
CMD ["python", "bot.py"]
