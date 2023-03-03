import os

prometheus_url = os.getenv('', 'http://prometheus.prometheus:9090')
teams_webhook = os.environ["teams_webhook"]
opsgenie_url = os.environ[""]
opsgenie_api_key = os.environ[""]