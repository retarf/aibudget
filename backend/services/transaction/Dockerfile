FROM python:3.14-slim

WORKDIR /app

# Install dependencies first so this layer is cached across code changes.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/__init__.py ./backend/__init__.py
COPY backend/common/ ./backend/common/
COPY backend/services/__init__.py ./backend/services/__init__.py
COPY backend/services/transaction/ ./backend/services/transaction/

CMD ["python", "-m", "backend.services.transaction.main"]
