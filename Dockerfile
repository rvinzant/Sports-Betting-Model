# Use an official lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements first to leverage Docker's cache
COPY requirements.txt .
RUN apt-get update && apt-get install -y libgomp1
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app's code
COPY . .

# Create logs directory if it doesn't exist
RUN mkdir -p logs

# Expose the port your app runs on
EXPOSE 8000

# Run the app
CMD ["python", "app.py"]
