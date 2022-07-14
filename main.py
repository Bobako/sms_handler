from sms_handler import app, service
import threading

if __name__ == '__main__':
    t1 = threading.Thread(target=service.run).start()
    t2 = threading.Thread(target=app.run).start()

