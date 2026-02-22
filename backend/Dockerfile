FROM python:3.11-slim

WORKDIR /app

# System deps for newspaper3k / lxml
RUN apt-get update && apt-get install -y \
    libxml2-dev libxslt-dev libffi-dev \
    gcc build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
