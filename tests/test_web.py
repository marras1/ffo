from io import BytesIO

from family_finance.web import WebApp


def _call(app, path='/', method='GET', data='', cookie=''):
    body = data.encode('utf-8')
    environ = {
        'PATH_INFO': path,
        'REQUEST_METHOD': method,
        'CONTENT_LENGTH': str(len(body)),
        'wsgi.input': BytesIO(body),
        'HTTP_COOKIE': cookie,
    }
    captured = {}

    def start_response(status, headers):
        captured['status'] = status
        captured['headers'] = headers

    chunks = app(environ, start_response)
    payload = b''.join(chunks).decode('utf-8', errors='ignore')
    return captured['status'], dict(captured['headers']), payload


def test_register_login_and_dashboard_access(tmp_path):
    app = WebApp(tmp_path / 'web.db')

    status, _, _ = _call(app, '/register', 'POST', 'username=anna&password=secret')
    assert status.startswith('302')

    status, headers, _ = _call(app, '/login', 'POST', 'username=anna&password=secret')
    assert status.startswith('302')
    cookie = headers['Set-Cookie'].split(';', maxsplit=1)[0]

    status, _, payload = _call(app, '/dashboard', 'GET', cookie=cookie)
    assert status.startswith('200')
    assert 'Welcome, anna' in payload
