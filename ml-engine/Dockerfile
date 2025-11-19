FROM python:3.9-slim
WORKDIR /app
# Copy requirements if exists, else create dummy
COPY requirements.txt* .
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
COPY . ml-engine/
ENV PYTHONPATH=/app
CMD ["python", "ml-engine/models/fraud_detector.py"]
