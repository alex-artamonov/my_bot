import config as c
import requests
import json
import os

def get_price(from_:str, to: str, amount: float):  #  дописать тип возврата
    API_KEY = os.environ['APILAYER']
    headers = {
        "apikey": API_KEY
    }
    url = f"https://api.apilayer.com/exchangerates_data/convert?to={to}&from={from_}&amount={amount}"
    response = requests.request("GET", url, headers=headers)
    status_code = response.status_code
    if status_code == 400:
        raise KeyError(f"Запрошенная информация {url} не найдена")
    result = response.text
    result = json.loads(result)
    return result['date'], result['result'], result['info']['rate']
