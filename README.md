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
