# Use Python 3.12 as the base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Poetry
RUN pip install --upgrade pip
RUN pip install poetry

# Install dependencies using Poetry
RUN poetry install --no-root

# Create necessary directories
RUN mkdir -p artifacts static/images

# Expose port 10000
EXPOSE 10000

# Command to run the application
CMD ["gunicorn", "src.app:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:10000"] 