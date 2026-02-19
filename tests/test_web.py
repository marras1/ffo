from io import BytesIO
from urllib.parse import urlencode

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


def test_manage_accounts_and_transactions_ui(tmp_path):
    app = WebApp(tmp_path / 'web.db')
    _call(app, '/register', 'POST', 'username=tom&password=secret')
    status, headers, _ = _call(app, '/login', 'POST', 'username=tom&password=secret')
    assert status.startswith('302')
    cookie = headers['Set-Cookie'].split(';', maxsplit=1)[0]

    account_payload = urlencode({'name': 'Checking', 'account_type': 'checking', 'opening_balance': '1000'})
    status, _, _ = _call(app, '/accounts', 'POST', account_payload, cookie=cookie)
    assert status.startswith('302')

    tx_payload = urlencode({'account_id': '1', 'kind': 'income', 'amount': '2500', 'description': 'Salary'})
    status, _, _ = _call(app, '/transactions', 'POST', tx_payload, cookie=cookie)
    assert status.startswith('302')

    status, _, payload = _call(app, '/dashboard', 'GET', cookie=cookie)
    assert status.startswith('200')
    assert 'Checking (checking): $3,500.00' in payload
    assert 'Salary' in payload
