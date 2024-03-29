import telebot
import config as c
import extentions as ext
from telebot import types
import os

TOKEN = os.environ["MONKEY"]
bot = telebot.TeleBot(TOKEN)
# username = 'my_test_parrot_bot'

currencies_str = "Валюты, с которыми я умею работать:\n" + \
                 "\n".join(sorted(f"- {key} : {value}" for key, value in c.currencies.items()))

commands = ['/start', '/help', '/convert', '/valuta', '/stop']

# для удобства пользователя сформируем словарь так, чтобы можно было
# указывать валюту и по-русски, и по коду валюты
currencies_complete = c.currencies.copy()
for key, value in c.currencies.items():
    currencies_complete.update({value.lower(): value})


def create_command_buttons():
    commands_markup = types.ReplyKeyboardMarkup(resize_keyboard=False)
    for command in commands:
        commands_markup.add(types.KeyboardButton(command))
    return commands_markup


def create_buttons(one_time_keyboard):
    # conv_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    conv_markup = types.ReplyKeyboardMarkup(one_time_keyboard=one_time_keyboard)
    buttons = []
    for val in c.currencies.keys():
        buttons.append(types.KeyboardButton(val.lower()))

    conv_markup.add(*buttons)
    return conv_markup


@bot.message_handler(commands=['start', 'help', 'stop', 'valuta'])
def send_welcome(message):
    cmd = message.text
    name = message.chat.first_name
    replies = {
        '/start': f'Приветствую, {name}!. Я - небольшой калькулятор валют '
                  f'на текущую дату. \nНажмите или напишите /convert для конвертации.\n'
                  f'Для более подробной информации, введите /help',
        '/help': f'Конвертирую (виртуально) из одной валюты в другую. Информация '
                 f'берется с сайта https://exchangerates.io.'
                 f'\nЧтобы пересчитать одну валюту в другую, введите запрос в формате'
                 f'\n\t<исходная валюта> <целевая валюта> <сумма в исходной валюте>, '
                 f'\nнапример, \n"евро рубль 100" \nили \n"eur rub 100"'
                 f'\nЛибо можно последовательно ввести'                 
                 f'\n<исходная валюта>'
                 f'\n<целевая валюта>'
                 f'\n<сумма в исходной валюте>'
                 f'\nСписок возможных валют можно получить, введя /valuta'
                 f'\nДля конвертации введите или выберете /convert',
        '/stop': f"Всего наилучшего, {name}",
        '/valuta': currencies_str
    }
    reply = replies[cmd]
    # bot.register_next_step_handler(message, convert_currency)
    bot.send_message(message.chat.id, reply, reply_markup=create_command_buttons())
    # if cmd == '/stop':
    #     # bot.stop_bot()  # ВЫЗЫВАЕТ ОШИБКУ!
    #     exit()


@bot.message_handler(commands=['convert'])
def command_convert(message):
    bot.send_message(message.chat.id, "Введите <исходная валюта> в отдельной строке либо "
                                      "<исходная валюта> <целевая валюта> <сумма> в одной строке:",
                     reply_markup=create_buttons(False))
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
                         parse_mode='HTML', reply_markup=create_command_buttons())
        else:
            bot.send_message(message.chat.id, "Введите, в какую валюту хотите пересчитать:",
                             reply_markup=create_buttons(True))
            bot.register_next_step_handler(message, handle_to, from_)

        return
    if len(list_to_parse) != 3:
        reply = "Извините, не понял - у меня маленький словарный запас и весьма" \
                " ограниченный круг задач.\nПопробуйте еще раз. Для справки нажмите /start или /help." \
                "\nЛибо /convert для пересчета из одной валюты в другую."
        bot.reply_to(message, reply, reply_markup=create_command_buttons())
        return
    #  вариант, когда введены сразу три значения
    from_input, to_input, amount_input = list_to_parse
    try:
        from_ = currencies_complete[from_input]
        to = currencies_complete[to_input]
        amount = float(amount_input.replace(",", "."))
    except ValueError:
        bot.reply_to(message, f"Не удалось распознать сумму <b>{amount_input}</b>"
                              f"\nПопробуйте еще раз, набрав или нажав /convert.", parse_mode="HTML",
                     reply_markup=create_command_buttons())
    except KeyError as e:
        bot.reply_to(message, f"Валюта <b>\"{e}\"</b> в базе не обнаружена."
                              f"\nПопробуйте еще раз, набрав или нажав /convert", parse_mode='HTML',
                     reply_markup=create_command_buttons())
    # except Exception as e:
    #     bot.reply_to(message, e)
    else:
        finalize(message, amount, from_, to)
        return


def handle_to(message, from_: str):
    """Обработка целевой валюты"""
    try:
        to = currencies_complete[message.text.lower()]
        if from_ == to:
            reply = "Целевая и исходная валюта одинаковы."
            bot.send_message(message.chat.id, reply, parse_mode='HTML')
            return

    except KeyError:
        bot.reply_to(message, f"Валюта <b>\"{message.text}\"</b> в базе не обнаружена."
                              f"\nПопробуйте еще раз, набрав или нажав /convert."
                              f"\nДля вывода списка валют наберите или нажмите /valuta", parse_mode="HTML",
                     reply_markup=create_command_buttons())
    else:
        bot.register_next_step_handler(message, handle_amount, from_, to)
        bot.send_message(message.chat.id, "Введите количество:")


def handle_amount(message, from_: str, to: str):
    """Обработка количества валюты"""
    try:
        amount = float(message.text.strip().replace(',', '.'))
    except ValueError:
        bot.reply_to(message, f"Не удалось распознать сумму <b>{message.text}</b>"
                              f"\nПопробуйте еще раз, набрав или нажав /convert.", parse_mode="HTML")
        # raise ValueError(f"Не удалось распознать сумму <b>{message.text}</b>"
        #                  f"\nПопробуйте еще раз, набрав или нажав /convert.")
    else:
        finalize(message, amount, from_, to)


def finalize(message, amount, from_, to):
    """Передает собранные данные для функции запроса на сайт"""
    try:
        date, result, rate = ext.get_price(from_, to, amount)
    except Exception as e:  # распарсить json ошибки!
        reply = f"Произошла ошибка:\n{e}"
        bot.reply_to(message, reply)
    else:
        reply = f"На дату {date} запрошенная сумма <b>{amount:.2f} {from_}</b> " \
                f"составляет:\n<b>{round(result, 2):.2f} {to}</b>\n" \
                f"по курсу {round(rate, 2):.2f} ({rate}) {to} за 1.00 {from_}."
        bot.send_message(message.chat.id, reply, parse_mode='HTML',
                         reply_markup=create_command_buttons())


@bot.message_handler(content_types=['text'])
def talk(message):
    bot.send_message(message.chat.id, "Для начала работы нажмите или введите"
                                      " /start или /help или /convert", reply_markup=create_command_buttons())


def start_bot():
    """запуск бота"""
    # commands_buttons()
    bot.polling()
