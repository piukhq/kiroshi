FROM ghcr.io/binkhq/python:3.11

WORKDIR /app

COPY ./basictest/run.py run.py

ENTRYPOINT [ "linkerd-await", "--" ]
CMD [ "python", "run.py" ]
