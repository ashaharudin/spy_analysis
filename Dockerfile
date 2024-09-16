# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir yfinance pandas

# Create a directory for output
RUN mkdir /app/output

# Run spy_analysis.py when the container launches
CMD ["python", "spy_analysis.py"]