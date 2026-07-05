# AI Academy API — container image for Azure Container Apps.
# Build from the repo root:  docker build -t academy-api .   (or: az acr build, see infra/)
FROM python:3.12-slim

WORKDIR /app

# Layer the workspace packages; data ships in the image (synthetic only — never real HR data).
COPY packages/ packages/
COPY apps/academy-api/ apps/academy-api/
COPY data/ data/

RUN pip install --no-cache-dir \
    ./packages/academy-core \
    ./packages/academy-services \
    ./packages/academy-scenarios-hrsd \
    ./apps/academy-api

ENV ACADEMY_DATA_DIR=/app/data \
    ACADEMY_RUNTIME=mock

# The ingress targetPort in infra/main.bicep must match this port.
EXPOSE 8000
CMD ["uvicorn", "academy_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
