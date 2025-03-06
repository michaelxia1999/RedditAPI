FROM ubuntu:latest

ENV PYTHONDONTWRITEBYTECODE=1
ENV ENV=prd
ENV DB_URL=postgresql+asyncpg://postgres:postgres@host.docker.internal:5432/postgres
ENV REDIS_HOST=host.docker.internal
ENV REDIS_PORT=6379
ENV REDIS_PWD=mypassword
ENV REDIS_DB=0
ENV JWT_KEY=secret
ENV JWT_ALGORITHM=HS256
ENV JWT_TTL_SEC=604800
ENV REFRESH_TOKEN_TTL_SEC=604800
ENV RATE_LIMIT=100

RUN apt-get update

RUN apt-get install -y curl

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Ensure the installed binary is on the PATH
ENV PATH="/root/.local/bin/:$PATH"

COPY pyproject.toml ./
COPY .python-version ./

COPY /app /app

WORKDIR /

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]