FROM ghcr.io/binkhq/python:3.11 as build
WORKDIR /src
ADD . .
RUN pip install poetry
RUN poetry build

FROM ghcr.io/binkhq/python:3.11
ARG PIP_INDEX_URL
WORKDIR /app
COPY --from=build /src/dist/*.whl .
RUN pip install *.whl && rm *.whl
COPY --from=build /src/alembic/ ./alembic/
COPY --from=build /src/alembic.ini .

ENTRYPOINT [ "linkerd-await", "--" ]
CMD [ "/usr/local/bin/kiroshi" ]
