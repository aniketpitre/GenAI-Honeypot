FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd -r -u 10001 app
COPY generator ./generator
COPY persona_config.json .
RUN mkdir /seed && chown 10001 /seed
USER 10001
ENTRYPOINT ["python", "-m", "generator.generate"]
CMD ["--output", "/seed"]
