FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY configs/ configs/
COPY assets/ assets/

ENV ROI_PORT=4006
EXPOSE 4006

CMD ["gunicorn", "--bind", "0.0.0.0:4006", "--workers", "2", "app:server"]
