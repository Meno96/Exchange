import requests


class Market:
    def __init__(self):
        self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

        self.params = {
            'start': '1',
            'limit': '1',
            'convert': 'USD'
        }

        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': '0535ae25-81e9-4e5d-8df1-8c6a20820c16'
        }

    def updated_data(self):
        database = requests.get(url=self.url, headers=self.headers, params=self.params).json()
        bitcoin_price = round(database['data'][0]['quote']['USD']['price'], 8)
        return bitcoin_price