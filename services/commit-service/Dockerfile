FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY ../../requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY . .

# Copy shared components from parent directory
COPY ../../services ./services
COPY ../../config ./config
COPY ../../utils ./utils

# Expose port
EXPOSE 8001

# Run the application
CMD ["python", "app.py"]
