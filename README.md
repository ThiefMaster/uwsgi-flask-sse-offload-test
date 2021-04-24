# uWSGI/Flask SSE Offloading

This is a small test for using uWSGI's offloading feature to run an SSE
notification hub (based on Redis' PubSub functionality) in a gevent
worker while running the rest of the Flask application directly in uWSGI
without involving gevent or async.

Based on [this article][uwsgi-offload-sse] in the uWSGI docs.

## Running it

- Create and activate a virtualenv
- `pip install -r requirements.txt`
- `uwsgi --ini uwsgi.ini`
- `uwsgi --ini uwsgi-offload.ini`
- Go to http://localhost:8000

[uwsgi-offload-sse]: https://uwsgi-docs.readthedocs.io/en/latest/articles/OffloadingWebsocketsAndSSE.html
