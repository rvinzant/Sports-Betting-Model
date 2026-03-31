# Set Python image
FROM python:3.11-slim

WORKDIR /app

# copy reqs first then rest of app code
COPY requirements.txt .
RUN apt-get update && apt-get install -y libgomp1
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# expose port
EXPOSE 8000

CMD ["python", "app.py"]
