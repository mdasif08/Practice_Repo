FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY services/repo-manager/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared components
COPY shared/ ./shared/

# Copy service code
COPY services/repo-manager/ .

# Expose port
EXPOSE 8002

# Run the service
CMD ["python", "app.py"]
