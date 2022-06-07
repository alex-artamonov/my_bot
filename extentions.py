import config as c
import requests
import json


def get_price(from_:str, to: str, amount: float):  #  дописать тип возврата
    headers = {
        "apikey": c.API_KEY
    }
    url = f"https://api.apilayer.com/exchangerates_data/convert?to={to}&from={from_}&amount={amount}"
    # payload = {}
    response = requests.request("GET", url, headers=headers)
    status_code = response.status_code
    print(f"{status_code=}")
    result = response.text
    # print(f"{result=}", type(result))
    result = json.loads(result)
    # print(f"{result=}")
    # [print(e, result[e]) for e in result]
    # print(f"{result['result']=}'\n'{result['date']=}'\n'{result['info']['rate']=}")
    return result['date'], result['result'], result['info']['rate']
    # return f"На дату {result['date']} запрошенная сумма <b>{amount} {from_}</b> " \
    #         f"составляет:\n<b>{result['result']} {to}</b>\n" \
    #         f"по курсу {result['info']['rate']} {to} за 1 {from_}."

class CurrencyNotFoundError(Exception):
    """При отсутствии значения, указанного пользователем в списке валют"""
    def __init__(self, currency: str):
        self.message = f"Извините,валюты {currency} в списке не найдено"
        # self.point = point
        super().__init__(self.message)

# class CurrencyNotFoundError(KeyError):
#     pass