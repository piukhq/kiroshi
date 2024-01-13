FROM ghcr.io/binkhq/python:3.12
ARG PIP_INDEX_URL
ARG APP_NAME
ARG APP_VERSION
RUN apt-get update && apt-get -y install gcc
RUN pip install --no-cache ${APP_NAME}==$(echo ${APP_VERSION} | cut -c 2-)
RUN apt-get -y remove gcc && apt-get -y autoremove && apt-get -y clean && rm -rf /var/lib/{apt,dpkg,cache,log}/
WORKDIR /app
ADD alembic/ alembic.ini /app/

ENTRYPOINT [ "linkerd-await", "--" ]
CMD [ "/usr/local/bin/kiroshi" ]
