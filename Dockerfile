FROM python:3.10-alpine
MAINTAINER Pascal Zimmermann <pascal.zimmermann@theiotstudio.com>

LABEL application="hana-injector" \
      description="hana-injector - Backend service to inject an MQTT Stream to a SAP Hana database" \
      version="0.0.1" \
      lastUpdatedBy="Pascal Zimmermann" \
      lastUpdatedOn="2022-10-31"

ENV HANA_INJECTOR_CONFIG_FILE_PATH="/image/config/config.yml"

COPY config/config.yml /image/config/config.yml
COPY injector /image/app/
COPY requirements.txt /image/app/

RUN addgroup -S -g 500 kubernetes && \
    adduser -S -u 500 -G kubernetes -h /home/kubernetes kubernetes && \
    apk --no-cache update && apk --no-cache upgrade && \
    apk --no-cache add gcc musl-dev && pip install --upgrade pip && \
    pip install -r /image/app/requirements.txt && \
    chown -R kubernetes:kubernetes /image/app && chmod -R +x /image/app && chmod +x /image/app/app.py && \
    rm /image/app/requirements.txt

EXPOSE 8080

USER 500

CMD ["python3","/image/app/app.py"]