# Fraud Detection Enterprise

A microservices-based fraud detection platform using Flask, React, Kafka, Flink, and Neo4j.

## Project Structure

- `backend/`: Flask REST API (User Auth, Fraud Analysis, Graph Visualization)
- `frontend/`: React + Vite Dashboard
- `ml-engine/`: Machine Learning models (Fraud Detector, Anomaly Detection)
- `streaming/`: Flink jobs for real-time processing
- `docker-compose.yml`: Infrastructure orchestration

## Prerequisites

- Docker & Docker Compose
- Python 3.9+ (for local dev)
- Node.js 18+ (for local dev)

## Quick Start (Docker)

1.  Build and start all services:
    ```bash
    docker-compose up --build
    ```
2.  Access the Dashboard:
    Open [http://localhost:3000](http://localhost:3000)
3.  Access the Backend API:
    [http://localhost:5000](http://localhost:5000)

## Local Development

### Backend

1.  Navigate to `backend/`:
    ```bash
    cd backend
    ```
2.  Create virtualenv and install dependencies:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # or .venv\Scripts\activate on Windows
    pip install -r requirements.txt
    ```
3.  Run the application:
    ```bash
    # Ensure you are in the project root
    export PYTHONPATH=$PYTHONPATH:.
    python backend/app/main.py
    ```

### Frontend

1.  Navigate to `frontend/`:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start dev server:
    ```bash
    npm run dev
    ```

## Features

- **Real-time Fraud Detection**: Analyzes transactions via Kafka stream.
- **Graph Analysis**: Visualizes relationships using Neo4j.
- **Dashboard**: Live alerts and statistics.
- 
<img width="1914" height="926" alt="Screenshot 2025-11-19 220805" src="https://github.com/user-attachments/assets/26f8f5e6-5f40-4ddc-8fcb-76d778145b26" />

<img width="1905" height="925" alt="Screenshot 2025-11-19 215313" src="https://github.com/user-attachments/assets/6da3f28e-0974-439e-b4fd-6e89bc4d5975" />

<img width="1907" height="925" alt="Screenshot 2025-11-19 220736" src="https://github.com/user-attachments/assets/babf4fa7-716b-433c-b9d2-031d96e2362b" />

<img width="1905" height="925" alt="Screenshot 2025-11-19 220751" src="https://github.com/user-attachments/assets/94b19a56-71ac-45cb-b35e-03d62030485d" />
