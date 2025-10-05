# Use a Spark base image with Python support
FROM spark:latest

# Set the working directory inside the container
WORKDIR /app

# Copy the Python script and its dependencies file
COPY transformations.py .
COPY requirements.txt .

# Switch to the root user to install packages
USER root

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Switch back to the non-root 'spark' user for security
USER spark

# Copy the data directory into the container
COPY data_skew/ ./data_skew/
