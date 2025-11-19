# Multi-stage Dockerfile for all services

# Stage 1: Flink Job
FROM flink:1.14.4-scala_2.11 AS flink-job
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-dev && \
    ln -s /usr/bin/python3 /usr/bin/python
RUN pip3 install apache-flink==1.14.4 kafka-python
COPY flink-job/job.py /opt/flink/usrlib/job.py

# Stage 2: Frontend
FROM node:16 AS frontend
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
EXPOSE 3000

# Stage 3: Prediction API
FROM python:3.9 AS prediction-api
WORKDIR /app
COPY prediction-api/requirements.txt .
RUN pip install -r requirements.txt
COPY prediction-api/ .
EXPOSE 5001

# Stage 4: Backend
FROM python:3.9 AS backend
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
EXPOSE 5000

# Stage 5: User Service
FROM python:3.9-slim AS user-service
WORKDIR /app
COPY user-service/requirements.txt .
RUN pip install -r requirements.txt
COPY user-service/ .



#Build commands:

# docker build --target flink-job -t fraud-detection-flink .
# docker build --target frontend -t fraud-detection-frontend .
# docker build --target prediction-api -t fraud-detection-prediction .
# docker build --target backend -t fraud-detection-backend .
# docker build --target user-service -t fraud-detection-user .


# Final Stage: Combine all services
FROM python:3.9-slim
WORKDIR /app
COPY --from=flink-job /opt/flink/usrlib/job.py /opt/flink/usrlib/job.py
COPY --from=frontend /app /app/frontend
COPY --from=prediction-api /app /app/prediction-api
COPY --from=backend /app /app/backend
COPY --from=user-service /app /app/user-service 
EXPOSE 3000 5000 5001
CMD ["sh", "-c", "cd /app/frontend && npm start & cd /app/backend && python app.py & cd /app/prediction-api && python api.py & cd /app/user-service && python user_service.py"]
