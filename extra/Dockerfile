# Use the official Bitnami Spark image as the base
FROM bitnami/spark:latest

# Set the working directory to /app
WORKDIR /app

# Copy the application code and any dependency files
# Note: The yml file has app mounted to /app, so we just need to make sure
# the files exist in the image for the spark-submit command to work.
COPY ./app/app.py /app/app.py

# The CMD instruction will be overridden by the `command` in the yml file,
# but it's good practice to have a default.
CMD ["spark-submit", "/app/app.py"]
