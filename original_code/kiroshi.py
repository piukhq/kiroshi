import time

import sentry_sdk

from kiroshi.kiroshi import checks

if __name__ == "__main__":
    try:
        while True:
            try:
                checks()
            except Exception:
                sentry_sdk.capture_exception()
            finally:
                time.sleep(60)
    except KeyboardInterrupt:
        pass