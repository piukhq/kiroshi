import logging
import settings

from kiroshi.request_retrys import requests_retry_session
from kiroshi.alerts import opsgenie, microsoft_teams

def check_prometheus():
    failures = 0
    call_out = 0
    session = requests_retry_session()
    try:
        response = session.get('http://prometheus.prometheus:9090/')
        if response.status_code == 200:
            if failures >=1:
                logging.info('Resetting number of failures to 0')
                failures = 0
                call_out = 0
            else:
                pass
    except:
        failures =+ 1
        if failures < 5:
            logging.error(f'Response from prometheus failed with code: {response.status_code}')
            message = f"Prometheus has been down for {failures} minutes"
            microsoft_teams(message)
        elif failures > 5 and failures < 10:
            if call_out >= 1:
                pass
            else:
                message = "Prometheus has been down for more than five minutes"
                microsoft_teams(message)
                opsgenie(message)
                logging.error(f'Response from prometheus failed with code: {response.status_code}')





def checks():
    check_prometheus()