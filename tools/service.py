import requests
import logging
import json
import time
from config import constants


class forex:
    def __init__(self, conf):
        self.conf = conf
        self.db = self.conf.dynamo_client
        self.table = self.conf.table_name
        self.rate_url = self.conf.rate_url
        self.app_id = self.conf.app_id

    def process(self):
        url = self.rate_url
        params = {"app_id": self.app_id, "symbols": constants.SYMBOLS}
        logging.info("Initiating forex rates extraction")
        response = requests.get(url, params=params)
        payload = json.loads(response.text)
        currencies = constants.CURRENCIES
        base = payload.get('base')
        rates = payload.get('rates')
        rate_timestamp = payload.get('timestamp')
        rate_date = time.strftime(constants.DATE_FORMAT, time.localtime(rate_timestamp))

        payload = []
        logging.info("Starting the payload creation for dynamo db")
        for currency in currencies:
            item = {'sell': {'S': base},
                    'pair': {'S': base+currency},
                    'rate': {'N': str(rates.get(currency))},
                    'buy': {'S': currency},
                    'rate_date': {'S': rate_date},
                    'rate_timestamp':{'S': rate_timestamp}}
            payload.append(item)
        logging.info("Inserting data into Dynamo DB")
        for item in payload:
            logging.info("Item inserted in dynamo db: "+ str(item))
            self.db.put_item(
                TableName=self.table,
                Item=item
            )
