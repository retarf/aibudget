FROM python:3.14-slim

WORKDIR /app

# Install dependencies first so this layer is cached across code changes.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
