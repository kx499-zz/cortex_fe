from flask import Flask


app = Flask(__name__)
app.config.from_object('config')


from app import views, models

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler

    #acces logs
    a_logger = logging.getLogger('werkzeug')
    handler = RotatingFileHandler('/tmp/access.log', 'a', 1 * 1024 * 1024, 10)
    a_logger.addHandler(handler)

    #error/app info logs
    file_handler = RotatingFileHandler('/tmp/app.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(module)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('App startup')




