import telebot
import config as c
import extentions as ext
from telebot import types


bot = telebot.TeleBot(c.TOKEN)
# username = 'my_test_parrot_bot'

currencies_str = "Валюты, с которыми я умею работать:\n" + \
                "\n".join(sorted(f"- {key} : {value}" for key, value in c.currencies.items()))

# для удобства пользователя сформируем словарь так, чтобы можно было
# указывать валюту и по-русски, и по коду валюты
currencies_complete = c.currencies.copy()
for key, value in c.currencies.items():
    currencies_complete.update({value.lower(): value})

def create_buttons():
    conv_markup = types.ReplyKeyboardMarkup(one_time_keyboard=False)
    buttons = []
    for val in c.currencies.keys():
        buttons.append(types.KeyboardButton(val.lower()))

    conv_markup.add(*buttons)


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
    bot.send_message(message.chat.id, reply, reply_markup=create_buttons())
    if cmd == '/stop':
        # bot.stop_bot()  # ВЫЗЫВАЕТ ОШИБКУ!
        exit()


@bot.message_handler(commands=['convert'])
def command_convert(message):
    bot.send_message(message.chat.id, "Введите <исходная валюта> в отдельной строке либо "
                                      "<исходная валюта> <целевая валюта> <сумма> в одной строке:",
                     reply_markup=create_buttons())
    bot.register_next_step_handler(message, convert_currency)


def convert_currency(message):
    #  и для случая, когда вводится по одному значению, и когда пользователь вводит сразу все
    #  в указанном формате
    txt = str(message.text).lower()
    list_to_parse = txt.split()

    # вариант для последовательного ввода значений:
    if len(list_to_parse) == 1:
        # если пользователь ввел
        try:
            from_ = currencies_complete[list_to_parse[0]]
        except KeyError:
            bot.reply_to(message, f"Валюта <b>\"{list_to_parse[0]}\"</b> в базе не обнаружена."
                       f"\nПопробуйте еще раз, набрав или нажав /convert."
                                  f"\nДля вывода списка валют наберите или нажмите /valuta",
                         parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "Введите, в какую валюту хотите пересчитать:")
            bot.register_next_step_handler(message, handle_to, from_)

        return
    if len(list_to_parse) != 3:
        reply = "Извините, не понял - у меня маленький словарный запас и весьма" \
                " ограниченный круг задач. \nПопробуйте еще раз. Для справки нажмите /start или /help." \
                "\nЛибо /convert для пересчета из одной валюты в другую."
        bot.reply_to(message, reply)
        return
    #  вариант, когда введены сразу три значения
    try:
        from_input, to_input, amount_input = list_to_parse
        from_ = currencies_complete[from_input]
        to = currencies_complete[to_input]
        amount = float(amount_input.replace(",", "."))
    except ValueError as e:
        bot.reply_to(message, f"Не удалось распознать сумму <b>{amount_input}</b>"
                     f"\nПопробуйте еще раз, набрав или нажав /convert.", parse_mode="HTML")
    except KeyError as e:
        bot.reply_to(message, f"Валюта <b>\"{e}\"</b> в базе не обнаружена."
                   f"\nПопробуйте еще раз, набрав или нажав /convert", parse_mode='HTML')
    # except Exception as e:
    #     bot.reply_to(message, e)
    else:
        finalize(message, amount, from_, to)
        return


def handle_to(message, from_: str):
    """Обработка целевой валюты"""
    try:
        to = currencies_complete[message.text.lower()]
    except KeyError as e:
        bot.reply_to(message, f"Валюта <b>\"{message.text}\"</b> в базе не обнаружена."
                       f"\nПопробуйте еще раз, набрав или нажав /convert."
                              f"\nДля вывода списка валют наберите или нажмите /valuta", parse_mode="HTML")
    else:
        bot.register_next_step_handler(message, handle_amount, from_, to)
        bot.send_message(message.chat.id, "Введите количество:")


def handle_amount(message, from_: str, to: str):
    """Обработка количества валюты"""
    try:
        amount = float(message.text.strip().replace(',','.'))
    except ValueError:
        bot.reply_to(message, f"Не удалось распознать сумму <b>{message.text}</b>"
                         f"\nПопробуйте еще раз, набрав или нажав /convert.", parse_mode="HTML" )
        # raise ValueError(f"Не удалось распознать сумму <b>{message.text}</b>"
        #                  f"\nПопробуйте еще раз, набрав или нажав /convert.")
    else:
        finalize(message, amount, from_, to)


def finalize(message, amount, from_, to):
    """передает собранные данные для функции запроса на сайт"""
    if from_ == to:
        reply = f"<b>{amount:.2f} {to} в {to}</b> в любой день и любую погоду будет " \
                f"<b>{amount:.2f} {to}</b>.\n" \
                f"Даже на сайт лезть не буду!"
        bot.send_message(message.chat.id, reply, parse_mode='HTML')
        return
    try:
        date, result, rate = ext.get_price(from_, to, amount)
    except Exception as e:  # распарсить json ошибки!
        reply = f"Произошла ошибка:\n{e}"
        bot.reply_to(message, reply)
    else:
        reply = f"На дату {date} запрошенная сумма <b>{amount:.2f} {from_}</b> " \
                f"составляет:\n<b>{round(result, 2):.2f} {to}</b>\n" \
                f"по курсу {round(rate, 2):.2f} ({rate}) {to} за 1.00 {from_}."
        bot.send_message(message.chat.id, reply, parse_mode='HTML')

@bot.message_handler(content_types=['text'])
def talk(message):
    bot.send_message(message.chat.id, "Для начала работы нажмите или введите"
                                      " /start или /help или /convert")

def start_bot():
    """запуск бота"""
    bot.polling()
    create_buttons()
