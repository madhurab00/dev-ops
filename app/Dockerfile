# Base Image
FROM python:3.11-slim

# Create a non-root user 
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser

# Working Directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Ownership
RUN chown -R appuser:appgroup /app

# Change Ownership
USER appuser

# Expose port 8000
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]