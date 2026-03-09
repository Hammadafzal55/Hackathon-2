# Install Python 3.11
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
