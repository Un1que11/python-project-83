from page_analyzer.app import client

import pytest


def test_main_page():
    response = client.get('/')

    assert response.status_code == 200

    with open('page_analyzer/templates/index.html') as f:
        assert b'<h1 class="display-3">Page analyzer</h1>' in response.data
