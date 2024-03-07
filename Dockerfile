# Use the official Python image as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Update the package lists for upgrades for packages that need upgrading, as well as new packages that have just come to the repositories
RUN apt-get update

# Install any needed packages specified in requirements.txt
RUN pip uninstall jwt
RUN pip install -y --no-cache-dir -r /app/requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV FLASK_APP=app.py

# Run flask when the container launches
#CMD ["flask", "run", "--host=0.0.0.0"]
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:80"]
