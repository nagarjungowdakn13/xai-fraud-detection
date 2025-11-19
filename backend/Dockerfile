FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . backend/
ENV PYTHONPATH=/app
CMD ["python", "backend/app/main.py"]
