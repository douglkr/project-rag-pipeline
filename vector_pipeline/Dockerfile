FROM python:3.11-slim

# Instal poppler
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy application files
COPY . .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
