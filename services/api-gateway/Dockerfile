FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY services/api-gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY services/api-gateway/ .

# Expose port
EXPOSE 8000

# Run the service
CMD ["python", "app.py"]
