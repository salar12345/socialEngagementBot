from db import init_db
from crud import create_or_update_profile
from social_fetcher import mock_fetcher

if __name__ == '__main__':
    init_db()
    create_or_update_profile('alice', 'mock', alert_threshold=1000)
    create_or_update_profile('bob', 'mock', alert_threshold=500)
    mock_fetcher.register('alice', initial=950)
    mock_fetcher.register('bob', initial=480)
    print('Demo setup done. Start the app with: uvicorn main:app --reload')
