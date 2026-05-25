FROM python:3.14-alpine3.23

LABEL org.opencontainers.image.title="hana-injector" \
      org.opencontainers.image.description="hana-injector - Backend service to inject an MQTT Stream to a SAP Hana database" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.authors="Pascal Zimmermann <pascal.zimmermann@theiotstudio.com>" \
      lastUpdatedBy="Pascal Zimmermann" \
      lastUpdatedOn="2026-05-24"

ENV HANA_INJECTOR_CONFIG_FILE_PATH="/image/config/config.yml"

COPY config/config.yml /image/config/config.yml
COPY injector /image/app/
COPY pyproject.toml /image/app/

RUN addgroup -S -g 500 injector && \
    adduser -S -u 500 -G injector -h /home/injector injector && \
    apk --no-cache update && apk --no-cache upgrade && \
    apk --no-cache add gcc musl-dev && \
    cd /image/app && pip install . && \
    chown -R injector:injector /image/app && chmod -R +x /image/app && chmod +x /image/app/app.py && \
    rm /image/app/pyproject.toml

EXPOSE 8080

USER 500

CMD ["python3","/image/app/app.py"]