# Use the official Python image as a base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip uninstall -y jwt && pip install --no-cache-dir -r /app/requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80
# For DEV environment
# EXPOSE 8080

# Define environment variable
ENV FLASK_APP=app.py
# For DEV environment
# ENV API_URL=https://eb448bc5-6b9f-4bde-9494-9e755fcad1c5.hanko.io
# ENV AUDIENCE=localhost

# Run flask when the container launches
# CMD ["flask", "run", "--host=0.0.0.0" , "--port=80"]
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:80"]
# For DEV environment
# CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8080"]