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
    bot.send_message(message.chat.id, "Введите <исходная валюта> в отдельной строке либо "
                                      "<исходная валюта> <целевая валюта> <сумма> в одной строке:")
    bot.register_next_step_handler(message, convert_currency)


# @bot.message_handler(content_types=['text'])
# @bot.message_handler(content_types=['text'])
def convert_currency(message):
    txt = str(message.text).lower()
    list_to_parse = txt.split()
    # убеждаемся, что пользователь ввел три слова
    if len(list_to_parse) == 1:
        print("hi from case 1")
        try:
            from_ = list_to_parse[0]
        except KeyError:
            bot.reply_to(message, f"Валюта <b>\"{to_input}\"</b> в базе не обнаружена."
                       f"\nПопробуйте еще раз, набрав или нажав /convert.", parse_mode='HTML')
        else:

            bot.send_message(message.chat.id, "Введите, в какую валюту хотите пересчитать:")
            bot.register_next_step_handler(message, handle_to, from_)
        # to = handle_to(message, message.text)
        # bot.send_message(message.chat.id, to)
        # bot.send_message(message.chat.id, "Введите количество:")
        #
        # bot.register_next_step_handler(message, handle_amount)
        # amount = handle_amount(message, message.text)
        # # bot.register_next_step_handler(message, handle_to())
        # # except:
        # finalize(message, amount, from_, to)
        return
    if len(list_to_parse) != 3:
        reply = "Извините, не понял - у меня маленький словарный запас и весьма" \
                " ограниченный круг задач. \nПопробуйте еще раз. Для справки нажмите /start или /help." \
                "\nЛибо /convert для пересчета из одной валюты в другую."
        bot.reply_to(message, reply)
        return
    else:
        print('hi from case 3')
        try:
            from_input, to_input, amount_input = list_to_parse
            # from_ = handle_from(message, from_input)
            # print(f"{from_=}")
            # to = handle_to(message, from_, to_input="")
            # print(f"from case 3 {to=}")
            # amount = handle_amount(message, amount_input)
            from_ = currencies_complete[from_input]
            to = currencies_complete[to_input]
            amount = float(amount_input.replace(",", "."))
        except ValueError:
            bot.send_message(f"Не удалось распознать сумму <b>{amount_input}</b>"
                         f"\nПопробуйте еще раз, набрав или нажав /convert.", parse_mode="HTML")
        except KeyError as e:
            bot.reply_to(message, f"Валюта <b>\"{e}\"</b> в базе не обнаружена."
                       f"\nПопробуйте еще раз, набрав или нажав /convert", parse_mode='HTML')
        # except Exception as e:
        #     bot.reply_to(message, e)
        else:
            finalize(message, amount, from_, to)





        #     amount = list_to_parse[0].replace(',', '.')
        #     amount = float(amount)
        # except ValueError:
        #     reply = f"Извините, не смог распознать число <b>{amount}</b>. Попробуйте еще раз.\n" \
        #             f"Для справки нажмите /help"
        #     bot.reply_to(message, reply, parse_mode='HTML')
        #     return
        # else:
        #     bot.register_next_step_handler(message, handle_from, amount)
        #     bot.send_message(message.chat.id, "Введите исходную валюту:")
        #     return

    # try:
    #     amount, from_, to = list_to_parse
    #     from_ = currencies_complete[from_]
    #     to = currencies_complete[to]
    #     amount = float(amount.replace(',', '.'))
    # except KeyError:
    #     reply = f"Извините, не нашел такой валюты. Для списка валют нажмите /valuta." \
    #             f"\nИ еще раз наберите или нажмите /convert"
    #     bot.reply_to(message, reply, parse_mode='HTML')
    #     return
    # except ValueError:
    #     reply = f"Извините, не смог распознать число <b>{amount}</b>. Попробуйте еще раз.\n" \
    #             f"Для справки нажмите /help"
    #     bot.reply_to(message, reply, parse_mode='HTML')
    #     return

        return
    # try:
    #     finalize(message, amount, from_, to)
    # except Exception as e:
    #     bot.reply_to(message, e)
    # try:
    #     date, result, rate = ext.get_price(from_, to, amount)
    # except Exception as e:
    #     reply = f"Произошла ошибка:\n{e}"
    #     # print('reply=', reply)
    #     bot.reply_to(message, reply)
    # else:
    #     reply = f"На дату {date} запрошенная сумма <b>{amount} {from_}</b> " \
    #             f"составляет:\n<b>{round(result, 2)} {to}</b>\n" \
    #             f"по курсу {round(rate, 2)} ({rate}) {to} за 1.00 {from_}."
    #     bot.reply_to(message, reply, parse_mode='HTML')

# @bot.message_handler(content_types=['text'])
# def handle_from(message):
#     try:
#         from_ = currencies_complete[message.text]
#         print("from handle_from: from:", from_)
#     except KeyError as e:
#         bot.reply_to(message, f"Валюта <b>\"{from_input}\"</b> в базе не обнаружена."
#                        f"\nПопробуйте еще раз, набрав или нажав /convert", parse_mode="HTML")
#         # bot.reply_to(message, f"Валюта <b>\"{from_input}\"</b> в базе не обнаружена. "
#         #                       f"Попробуйте еще раз.", parse_mode='HTML')
#         # bot.reply_to(message, f"<b>{e}</b>", parse_mode='HTML')
#     else:
#         # bot.send_message(message.chat.id, 'Укажите, в какую валюту пересчитываем')
#         bot.register_next_step_handler(message, handle_to, from_)


# @bot.message_handler(content_types=['text'])
def handle_to(message, from_: str):
    try:
        to = currencies_complete[message.text]
    except KeyError as e:
        raise KeyError(f"Валюта <b>\"{to_input}\"</b> в базе не обнаружена."
                       f"\nПопробуйте еще раз, набрав или нажав /convert.")
        # bot.reply_to(message, f"Валюта <b>\"{to_input}\"</b> в базе не обнаружена. "
        #                       f"Попробуйте еще раз.", parse_mode='HTML')
    else:
        bot.register_next_step_handler(message, handle_amount, from_, to)
        bot.send_message(message.chat.id, "Введите количество:")
    # bot.send_message(message.chat.id, "Укажите целевую валюту")
    #     bot.send_message(message.chat.id, f"{amount=}, {from_=}, {to=}")
    #     finalize(message, amount, from_, to)


def handle_amount(message, from_: str, to: str):
    # amount_input = message.text
    try:
        amount = float(message.text.strip().replace(',','.'))
    except ValueError:
        raise ValueError(f"Не удалось распознать сумму <b>{message.text}</b>"
                         f"\nПопробуйте еще раз, набрав или нажав /convert.")
        # bot.reply_to(message, f"Ну удалось распознать сумму <b>{amount_input}</b>"
        #                       f"\nПопробуйте еще раз.", parse_mode='HTML')
    else:
        finalize(message, amount, from_, to)


def finalize(message, amount, from_, to):
    if from_ == to:
        reply = f"<b>{amount:.2f} {to} в {to}</b> в любой день и любую погоду будет " \
                f"<b>{amount:.2f} {to}</b>.\n" \
                f"Даже на сайт лезть не буду!"
        bot.send_message(message.chat.id, reply, parse_mode='HTML')
        return
    # print(f"{message.chat.id=}")
    try:
        date, result, rate = ext.get_price(from_, to, amount)
    except Exception as e:  # распарсить json ошибки!
        reply = f"Произошла ошибка:\n{e}"
        # print('reply=', reply)
        bot.reply_to(message, reply)
    else:
        reply = f"На дату {date} запрошенная сумма <b>{amount} {from_}</b> " \
                f"составляет:\n<b>{round(result, 2)} {to}</b>\n" \
                f"по курсу {round(rate, 2)} ({rate}) {to} за 1.00 {from_}."
        bot.send_message(message.chat.id, reply, parse_mode='HTML')

@bot.message_handler(content_types=['text'])
def talk(message):
    bot.send_message(message.chat.id, "Для начала работы нажмите или ввеите"
                                      " /start или /help или /convert")

bot.polling()
