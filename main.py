"""App entry point. If 'autosend' keyword in sys.argv app will
automatically resend all unsuccessful messages from primary service """
import sys
import threading

from sms_handler import app, sms_api_worker, config

if __name__ == '__main__':
    if "autosend" in sys.argv:
        sms_api_worker_thread = threading.Thread(target=sms_api_worker.run).start()
    app_thread = threading.Thread(target=app.run, kwargs={"port": int(config["SITE"]["port"])}).start()
