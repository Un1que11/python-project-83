from page_analyzer.app import client


def test_main_page():
    response = client.get('/')

    assert response.status_code == 200
    assert b'<h1 class="display-3">Page analyzer</h1>' in response.data


def test_urls_page():
    response = client.get('/urls')

    assert response.status_code == 200
    assert b'<h1>Sites</h1>' in response.data


def test_url_page():
    response = client.get('/urls/1')

    assert response.status_code == 200
