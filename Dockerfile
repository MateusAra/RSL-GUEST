FROM node:20-slim AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY alembic.ini ./
COPY migrations ./migrations
COPY src ./src
COPY --from=web /web/dist ./web/dist

ENV PYTHONPATH=/app/src \
    RSL_STORAGE_PATH=/data/storage
EXPOSE 8000
CMD ["uvicorn", "rsl.app:app", "--host", "0.0.0.0", "--port", "8000"]
