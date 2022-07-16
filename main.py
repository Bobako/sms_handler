from sms_handler import app, sms_api
import threading

if __name__ == '__main__':
    t1 = threading.Thread(target=sms_api.run).start()
    t2 = threading.Thread(target=app.run).start()

