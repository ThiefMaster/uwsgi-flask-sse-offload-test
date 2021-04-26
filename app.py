from flask import Flask, render_template, request
from redis import StrictRedis

app = Flask(__name__)
app.debug = True
redis = StrictRedis('localhost', 6379, db=0)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/subscribe')
def subscribe():
    try:
        import uwsgi
    except ImportError:
        # If we're not running inside uWSGI, we make use of the fact that
        # the response of a Flask view can also be another WSGI application,
        # and while not being particularly scalable, we can run the SSE app
        # within the Flask dev server.
        import sseapp
        def _app(environ, start_response):
            environ['OFFLOAD_USER_IP'] = request.remote_addr
            return sseapp.application(environ, start_response)
        return _app

    # If we are running inside uWSGI, ask it to offload the request to the
    # gevent-based instance which only runs the SSE app.
    uwsgi.add_var('OFFLOAD_TO_SSE', 'y')
    uwsgi.add_var('OFFLOAD_SERVER', '/tmp/uwsgi-offload.sock')
    uwsgi.add_var('OFFLOAD_USER_IP', request.remote_addr)
    return app.response_class('', mimetype='text/event-stream')


@app.route('/publish', methods=('POST',))
def publish():
    msg = request.form['msg']
    redis.publish('events', msg)
    return '', 204
