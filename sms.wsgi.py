#!/var/www/SMS/venv/python
import sys
import logging
import threading

from sms_handler import app, service

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/SMS/")

t1 = threading.Thread(target=service.run).start()
t2 = threading.Thread(target=app.run).start()
