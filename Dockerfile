FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Chromium and its system dependencies
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

# Non-root user
RUN useradd --create-home appuser
USER appuser

CMD ["python", "tests/test_login.py"]