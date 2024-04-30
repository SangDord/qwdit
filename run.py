from qwdit import app
from waitress import serve
import logging
from paste.translogger import TransLogger

logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)

HOST = '127.0.0.1'
PORT = 8080

#app.run(host=HOST, port=PORT)
serve(TransLogger(app, setup_console_handler=False), host=HOST, port=PORT)