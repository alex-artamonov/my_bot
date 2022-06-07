import telebot
import config as c
import extentions as ext


bot = telebot.TeleBot(c.TOKEN)
# username = 'my_test_parrot_bot'

currencies_str = "Валюты, с которыми я умею работать:\n" + \
                "\n".join(sorted(f"- {key} : {value}" for key, value in c.currencies.items()))

# для удобства пользователя сформируем словарь так, чтобы можно было
# указывать валюту и по-русски, и по коду валюты
currencies_complete = c.currencies.copy()
for key, value in c.currencies.items():
    currencies_complete.update({value.lower(): value})

# print(currencies_complete)

@bot.message_handler(commands=['start', 'help', 'stop', 'valuta'])
def send_welcome(message):
    cmd = message.text
    name = message.chat.first_name
    replies = {
        '/start': f'Приветствую, {name}!. Я - небольшой калькулятор валют '
                  f'на текущую дату. Для более подробной информации, введите /help',
        '/help': f'Конвертирую (виртуально) из одной валюты в другую. Информация '
                 f'берется с сайта https://exchangerates.io.'
                 f'\nЧтобы пересчитать одну валюту в другую, введите запрос в формате'
                 f'\n\t<сумма в исходной валюте> <исходная валюта> <целевая валюта> , '
                 f'\nнапример, \n"100 евро рубль" \nили \n"100 eur rub"'
                 f'\nЛибо можно последовательно ввести'
                 f'\n<сумма в исходной валюте>'
                 f'\n<исходная валюта>'
                 f'\n<целевая валюта>'
                 f'\nСписок возможных валют можно получить, введя /valuta'
                 f'\nДля конвертации введите или выберете /convert',
        '/stop': f"Всего наилучшего, {name}",
        '/valuta': currencies_str
    }
    reply = replies[cmd]
    bot.send_message(message.chat.id, reply)
    if cmd == '/stop':
        # bot.stop_bot()  # ВЫЗЫВАЕТ ОШИБКУ!
        exit()

@bot.message_handler(commands=['convert'])
def command_convert(message):
    bot.send_message(message.chat.id, "Введите <сумма> либо <сумма> "
                                      "<исходная валюта> <целевая валютаБ:")
    bot.register_next_step_handler(message, convert_currency)


# @bot.message_handler(content_types=['text'])
@bot.message_handler(content_types=['text'])
def convert_currency(message):
    txt = str(message.text).lower()
    list_to_parse = txt.split()
    # убеждаемся, что пользователь ввел три слова
    if len(list_to_parse) == 1:
        bot.register_next_step_handler(message, handle_from, list_to_parse[0])
        bot.send_message(message.chat.id, "Введите исходную валюту:")
        return
    if len(list_to_parse) != 3:
        reply = "Извините, не понял - у меня маленький словарный запас и весьма" \
                " ограниченный круг задач. \nПопробуйте еще раз. Для справки нажмите /start или /help."
        bot.reply_to(message, reply)
        return
    try:
        amount, from_, to = list_to_parse
        from_ = currencies_complete[from_]
        to = currencies_complete[to]
        amount = float(amount.replace(',', '.'))
    except KeyError:
        reply = f"Извините, не нашел такой валюты. Для списка валют нажмите /valuta."
        bot.reply_to(message, reply, parse_mode='HTML')
        return
    except ValueError:
        reply = f"Извините, не смог распознать число <b>{amount}</b>. Попробуйте еще раз.\n" \
                f"Для справки нажмите /help"
        bot.reply_to(message, reply, parse_mode='HTML')
        return
    if from_ == to:
        reply = f"<b>{amount} {to} в {to}</b> в любой день и любую погоду будет {amount} {to}.\n" \
                f"Даже на сайт лезть не буду!"
        bot.reply_to(message, reply, parse_mode='HTML')
        return
    finalize(message, amount, from_, to)
    # try:
    #     date, result, rate = ext.get_price(from_, to, amount)
    # except Exception as e:
    #     reply = f"Произошла ошибка:\n{e}"
    #     # print('reply=', reply)
    #     bot.reply_to(message, reply)
    # else:
    #     reply = f"На дату {date} запрошенная сумма <b>{amount} {from_}</b> " \
    #             f"составляет:\n<b>{round(result, 2)} {to}</b>\n" \
    #             f"по курсу {round(rate, 2)} ({rate}) {to} за 1,00 {from_}."
    #     bot.reply_to(message, reply, parse_mode='HTML')

@bot.message_handler(content_types=['text'])
def handle_from(message, amount):
    try:
        from_ = currencies_complete[message.text]
    except KeyError as e:
        # bot.reply_to(message, f"Валюта <b>\"{message.text}\"</b> в базе не обнаружена. "
        #                       f"Попробуйте еще раз.", parse_mode='HTML')
        bot.reply_to(message, f"<b>{e}</b>", parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, 'Укажите целевую валюту')
        bot.register_next_step_handler(message, handle_to, amount, from_)

@bot.message_handler(content_types=['text'])
def handle_to(message, amount, from_):
    to = currencies_complete[message.text]
    # bot.send_message(message.chat.id, "Укажите целевую валюту")
    bot.send_message(message.chat.id, f"{amount=}, {from_=}, {to=}")
    finalize(message, amount, from_, to)

def finalize(message, amount, from_, to):
    print(f"{message.chat.id=}")
    try:
        date, result, rate = ext.get_price(from_, to, amount)
    except Exception as e:
        reply = f"Произошла ошибка:\n{e}"
        # print('reply=', reply)
        bot.reply_to(message, reply)
    else:
        reply = f"На дату {date} запрошенная сумма <b>{amount} {from_}</b> " \
                f"составляет:\n<b>{round(result, 2)} {to}</b>\n" \
                f"по курсу {round(rate, 2)} ({rate}) {to} за 1 {from_}."
        bot.send_message(message.chat.id, reply, parse_mode='HTML')


bot.polling()
