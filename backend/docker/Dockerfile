# Use the official Python image from the Docker Hub
FROM python:3.13

# Set environment variables to ensure that Python outputs everything that's printed inside the application directly to the terminal
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy the requirements file into the container at /usr/src/app/
COPY requirements.txt /app/

# Install the dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

#Copy several shell scripts and make them executable in one layer
COPY start /usr/bin/
RUN chmod +x /usr/bin/start

COPY . /app/

ENTRYPOINT ["start"]
