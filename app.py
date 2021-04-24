import uwsgi
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
    uwsgi.add_var('OFFLOAD_TO_SSE', 'y')
    uwsgi.add_var('OFFLOAD_SERVER', '/tmp/uwsgi-offload.sock')
    uwsgi.add_var('OFFLOAD_USER_IP', request.remote_addr)
    return app.response_class('', mimetype='text/event-stream')


@app.route('/publish', methods=('POST',))
def publish():
    msg = request.form['msg']
    redis.publish('events', msg)
    return '', 204
