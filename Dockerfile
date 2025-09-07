FROM python:3.10-slim

WORKDIR /src
COPY . .

# Install any needed packages specified in requirements.txt 
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]