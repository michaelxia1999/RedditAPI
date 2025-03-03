# FastAPI Backend with Docker and uv

## Overview

This project is a FastAPI-based backend designed for high-performance web applications. It leverages `uv` for Python package management and `Docker` for containerization, ensuring a consistent development and deployment environment.

### Features
- **FastAPI Framework** - High-performance backend with automatic OpenAPI documentation.
- **uv Package Manager** - Efficient dependency and virtual environment management.
- **PostgreSQL & Redis** - Database and caching layer with Docker Compose.
- **Dockerized Environment** - Easily reproducible setup for development and deployment.
- **Integration Testing** - Test suite using `pytest` with environment-specific configurations.

---

## Prerequisites

Ensure you have the following installed before proceeding:

1. **[uv](https://github.com/astral-sh/uv)** - Python package and project manager
2. **[Docker](https://www.docker.com/)** - Containerization platform

---

## Running the Application in Development Mode

Follow these steps to start the application in development mode:

1. **Start Redis and PostgreSQL containers**  
   ```sh
   docker compose up
   ```
2. **Run the FastAPI server**  
   ```sh
   uv run --env-file dev.env uvicorn app.main:app --reload
   ```
3. **Open API Documentation**  
   Navigate to: [http://localhost:8000/docs](http://localhost:8000/docs)

4. **Run Integration Tests**  
   ```sh
   uv run --env-file test.env pytest tests -s
   ```

---

## Deployment Instructions

To deploy the application using Docker:

1. **Build the Docker image**  
   ```sh
   docker build -t app-image .
   ```
2. **Run the container**  
   ```sh
   docker run -p 8000:80 --name app-container app-image
   ```
3. **Access API Documentation**  
   Navigate to: [http://localhost:8000/docs](http://localhost:8000/docs)

---