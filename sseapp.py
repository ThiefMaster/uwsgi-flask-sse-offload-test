from redis import RedisError, StrictRedis

redis = StrictRedis('localhost', 6379, db=0)


def _sse(event, data=None):
    parts = [f'event: {event}', f'data: {data or ""}']
    return ('\r\n'.join(parts) + '\r\n\r\n').encode()


def application(environ, start_response):
    # The IP is just here to test passing data from the main app
    ip = environ['OFFLOAD_USER_IP']
    print(f'New connection from {ip}')
    start_response('200 OK', [
        ('Content-Type', 'text/event-stream'),
        ('Cache-Control', 'no-cache'),
    ])
    with redis.pubsub() as pubsub:
        pubsub.subscribe('events')
        while True:
            try:
                msg = pubsub.get_message(timeout=60)
                if not msg:
                    # send a ping from time to time; this will result in a GeneratorExit
                    # in case the client disconnected so we can stop listening
                    yield _sse('ping')
                    continue
                if msg['type'] != 'message' or msg['channel'].decode() != 'events':
                    continue
                data = msg['data'].decode()
                yield _sse('message', data)
            except RedisError as exc:
                # SSE clients reconnect, so we don't need to try to recover
                print(f'Redis error: {exc}')
                break
            except GeneratorExit:
                break
    print(f'{ip} disconnected')
