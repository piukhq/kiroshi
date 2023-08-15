FROM ghcr.io/binkhq/python:3.11

WORKDIR /app

COPY . .

ENTRYPOINT [ "linkerd-await", "--shutdown", "--" ]
CMD [ "python", "run.py" ]
