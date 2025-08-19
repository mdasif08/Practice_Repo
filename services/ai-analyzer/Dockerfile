FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY services/ai-analyzer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared components
COPY shared/ ./shared/

# Copy service code
COPY services/ai-analyzer/ .

# Expose port
EXPOSE 8004

# Run the service
CMD ["python", "app.py"]
