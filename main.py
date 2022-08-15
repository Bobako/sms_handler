"""App entry point. If 'auto_send' keyword in sys.argv app will
automatically resend all unsuccessful messages from primary service """
import sys
import threading

from sms_handler import app, sms_api_worker, config

if __name__ == '__main__':
    # sms_api_worker_thread = threading.Thread(target=sms_api_worker.run,
    #                                         kwargs={"auto_send": "auto_send" in sys.argv}).start()
    # disabled in demo
    app_thread = threading.Thread(target=app.run, kwargs={"port": int(config["SITE"]["port"])}).start()
