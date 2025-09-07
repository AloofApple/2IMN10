FROM python:3.10-slim

WORKDIR /src

# Copy the current directory contents into the container at /src
COPY . .

# Install any needed packages specified in requirements.txt 
RUN pip install --no-cache-dir -r requirements.txt

# Define environment variables
# ENV NAME World

CMD ["python", "app.py"]