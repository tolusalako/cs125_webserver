from sanic import Sanic
import log
from . import main, security
from .exception import handler

import config

logger = log.get_logger(__name__)

app = Sanic("CS125")
security.Security(app)
handler.CustomException(app)
app.log = logger
app.blueprint(main.bp)

def start(loop = None):
    logger.info("Starting api server...")
    app.run(host=config.host, port=8000, workers=config.workers, debug=True, loop=loop)
