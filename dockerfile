FROM python:3.10.15-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install any dependencies
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY ./web .

# Specify the command to run on container start
CMD [ "python", "./main.py" ]