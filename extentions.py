import config as c
import requests
import json


def get_price(from_:str, to: str, amount: float):  #  дописать тип возврата
    headers = {
        "apikey": c.API_KEY
    }
    url = f"https://api.apilayer.com/exchangerates_data/convert?to={to}&from={from_}&amount={amount}"
    response = requests.request("GET", url, headers=headers)
    status_code = response.status_code
    if status_code == 400:
        raise KeyError("запрошенная информация не найдена")
    print(f"{status_code=}")
    result = response.text
    result = json.loads(result)
    return result['date'], result['result'], result['info']['rate']
