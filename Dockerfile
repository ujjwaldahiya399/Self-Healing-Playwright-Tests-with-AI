FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install-deps chromium

COPY . .

RUN useradd --create-home appuser
USER appuser

RUN playwright install chromium

CMD ["python", "tests/test_login.py"]