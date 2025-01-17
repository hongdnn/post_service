# Use the official Python image as a base image
FROM python:3.12.5

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . /app/

# Expose the port the app runs on
EXPOSE 5001

# Command to run the application
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "5001", "--log-level", "info"]
