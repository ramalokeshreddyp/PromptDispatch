FROM python:3.12-slim

LABEL maintainer="chdsssbaba"
LABEL description="AI-powered prompt router for intent classification"

WORKDIR /app

# Install deps first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
