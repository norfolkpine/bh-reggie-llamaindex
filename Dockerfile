# Use Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy code and requirements first (better caching)
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Expose port (Cloud Run default)
EXPOSE 8080

# Run the app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
