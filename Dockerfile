FROM python:3.11

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

# Copy the requirements file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot code to the container
COPY . .

# Attach the volume to the container
VOLUME ./files

# Set the entrypoint command to run the bot
CMD ["python", "main.py"]