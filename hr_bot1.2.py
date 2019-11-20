#HR bot 1.2

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, Filters

from db_bot import *
from states_bot import *
import states_bot
# from menu import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


#MAIN BODY

raise Bot_Exception('Exception raised', 'Произошла ошибка. Необходимо заполнить заново')

def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text='Пожалуйста, введите код идентификации:')
    print('start')
    return AUTHENTIFICATION

def check_pass(password):
    if password=="1234":
        return "user"
    elif password=="7890":
        return "admin"
    else:
        return "error"

def authentification(update, context):
    print('authentification')
    user_id = update.message.from_user.id
    create_new_user(user_id)
    res = check_pass(update.message.text)
    if res == "admin":
        update.message.reply_text('Вы вошли как администратор')
        return AS_ADMIN
    elif res == "user":
        if  check_user(update.message.from_user.id, dict_keys_decoder.keys()):
            last_order = get_last_order(user_id)
            step_id = last_order['order_step_id']
            step = get_info_dialogue_step(step_id)
            txt = step['text']
            menu = step['menu']
            if step_id == 1:
                update.message.reply_text(txt, reply_markup=create_menu(menu))
                return AS_USER
            else:
                update.message.reply_text('У вас есть незавершенный запрос. Вы хотите продолжить его заполнение?', reply_markup=create_menu(filling_out_order_list))
                return RESTART_ORDER
        else:
            return new_user(update, context)
    else:
        update.message.reply_text('Указанный код не подходит')
        return AUTHENTIFICATION

def create_menu(list_of_lists):
    list_button = []
    for line in list_of_lists:
        list_button_2 = []
        for button in line:
            list_button_2.append(InlineKeyboardButton(button['text'], callback_data=button['value']))
        list_button.append(list_button_2)
    return InlineKeyboardMarkup(list_button)

def restart_order(update, context):
    query = update.callback_query
    user_id = update.callback_query.from_user.id
    print(type(query))
    if query['data'] == str(CONTINUE_FILLING): #Yes
        last_order = get_last_order(user_id)
        step_id = last_order['order_step_id']
        step = get_info_dialogue_step(step_id)
        pass
    elif query['data'] == str(STOP_FILLING): #No
        delete_order_by_user_id(user_id)
        query.edit_message_reply_markup(text='Выберите действие:', reply_markup=create_menu(main_menu_list))
        return AS_USER

def new_user(update, context):
    user_id = update.message.from_user.id
    if check_user(user_id, dict_keys_decoder.keys()):
        update.message.reply_text('Регистрация пользователя завершена. \nВыберите действие:', reply_markup=create_menu(main_menu_list))
        return AS_USER
    else:
        anticipating = get_anticipated_info(user_id)
        if anticipating != None:
            value = update.message.text
            get_user_data_to_db(anticipating, value, user_id)
        keys = missing_keys(user_id, dict_keys_decoder.keys())
        keys.sort()
        if len(keys) > 0:
            set_anticipated_info(user_id, keys[0])
            context.bot.send_message(chat_id=update.message.chat_id, text=decode_keys_to_msg(keys[0]))
            return NEW_USER
        else:
            update.message.reply_text('Регистрация пользователя завершена. \nВыберите действие:', reply_markup=create_menu(main_menu_list))
            return AS_USER

def change_personal_info_options(update, context):
    print('pi options menu')
    query = update.callback_query
    user_id = update.callback_query.from_user.id
    print(update.callback_query)
    f, n, o, t = show_personal_info(user_id)
    query.edit_message_text(text="Сейчас у нас есть следующая информация о вас:\n\
Фамилия - {0}\nИмя - {1}\nОтчество - {2}\nМобильный телефон - +7{3}\nКакую информацию о себе вы хотите изменить?".format(f, n, o, t))
    query.edit_message_reply_markup(text='Какую информацию о себе вы хотите изменить?', reply_markup=create_menu(change_pi_menu_list))
    print('pi list to user')
    return SAVE_PI_TO_CHANGE

def save_pi_to_change(update, context):
    query = update.callback_query
    user_id = update.callback_query.from_user.id
    query.edit_message_text(text=dict_keys_decoder[query['data']])
    set_anticipated_info(user_id, query['data'])
    return NEW_PI_TO_DB

def change_personal_info_to_db(update, context):
    print('add user pi changes to db')
    user_id = update.message.from_user.id
    anticipating = get_anticipated_info(user_id)
    value = update.message.text
    get_user_data_to_db(anticipating, value, user_id)
    f, n, o, t = show_personal_info(user_id)
    update.message.reply_text("Сейчас у нас есть следующая информация о вас:\n\
Фамилия - {0}\nИмя - {1}\nОтчество - {2}\nМобильный телефон - +7{3}\n".format(f, n, o, t))
    update.message.reply_text('Изменение персональных данных завершено. \nВыберите действие:', reply_markup=create_menu(main_menu_list)) #
    return AS_USER

def get_HR_contacts(update, context):
    query = update.callback_query
    query.edit_message_text(text="HR contacts: <...>")
    query.edit_message_reply_markup(reply_markup=create_menu(main_menu_list))
    print("get_HR_contacts")
    return AS_USER

def get_document_copy_option(update, context):
    print("get_document_copy_option")
    user_id = update.callback_query.from_user.id
    set_document_copy_to_db(user_id)
    context.bot.send_message(chat_id=update.callback_query.message.chat.id, text='Укажите, сколько копий документов необходимо:')
    return DOCUMENTS_AMOUNT_SET_BY_USER

def set_documents_amount(update, context):
    amount = update.message.text
    user_id = update.message.from_user.id
    print('amount of docs: ' + amount)
    set_documents_amount_to_db(user_id, amount)
    type, amount, subtype, period = show_order_info(user_id)
    if type == 'copy':
        type = 'Копия трудовой книжки'
        update.message.reply_text("Сейчас у нас есть следующая информация о вашем запросе:\n\
Тип необходимого документа - {0}\nКоличество копий - {1}\n".format(type, amount))
    elif type == 'info_sheet':
        type = 'Справка'
        update.message.reply_text("Сейчас у нас есть следующая информация о вашем запросе:\n\
Тип необходимого документа - {0}\nПодтип - {1}\nКоличество копий - {2}\nПериод - {3}".format(type, subtype, amount, period))
    context.bot.send_message(chat_id=update.message.chat_id, text='Где вы хотите получить документы:', reply_markup=create_menu(location_choice_list))
    return GET_LOCATION

# def get_location(update, context):
#     print("GET_LOCATION")
#     query = update.callback_query
#     user_id = update.callback_query.from_user.id
#     location = get_loc_by_id(query['data'])
#     if location != None and 'name' in location:
#         set_location_to_db(user_id,  location['name']+ (', ' + location['address']) if 'address' in location else "")
#         type, amount, subtype, period = show_order_info(user_id)
#         if type == 'copy':
#             type = 'Копия трудовой книжки'
#             query.edit_message_text(text="Сейчас у нас есть следующая информация о вашем запросе:\n\
# Тип необходимого документа - {0}\nКоличество копий - {1}\nМесто выдачи - {2}\n".format(type, amount, location))
#         elif type == 'info_sheet':
#             type = 'Справка'
#             query.edit_message_text(text="Сейчас у нас есть следующая информация о вашем запросе:\n\
# Тип необходимого документа - {0}\nПодтип - {1}\nКоличество копий - {2}\nПериод - {3}\nМесто выдачи - {4}\n".format(type, subtype, amount, period, location))
#         context.bot.send_message(chat_id=update.message.chat_id, text='Проверьте, пожалуйста, правильность запроса.\n\
# Запрос проверен и его можно отдавать в работу?', reply_markup=reply_markup=create_menu(order_finalization_list))
#     else:
#         query.edit_message_text(text="Мы не распознали адрес. Выберите снова.")
#         print("GET_LOCATION2")
#         return GET_LOCATION

#check if order is ok
def check_final_order(update, context):
    query = update.callback_query
    user_id = update.callback_query.from_user.id
    if query['data'] == str(FINAL_WORDS):
        transfer_order_to_inprocess(user_id)
        return FINAL_WORDS
    elif query['data'] == str(STOP_FILLING):
        delete_order_by_user_id(user_id)
        query.edit_message_reply_markup(text='Выберите действие:', reply_markup=create_menu(main_menu_list))
        return AS_USER

def final_words(update, context):
    print("final_words") #not query
    # query = update.callback_query
    # query.edit_message_text(text="Ваш запрос сформирован и отправлен в HR. Спасибо за использование услуг бота. Можете разместить следующий запрос. ")
    # query.edit_message_reply_markup(reply_markup=create_menu(main_menu_list))
    return AS_USER



def get_info_sheet_all_options(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    set_info_sheet_to_db(user_id)
    query.edit_message_reply_markup(text="Какую справку вы хотите получить", reply_markup=create_menu(info_sheet_options_list))
    print("info_sheet_options")

def choice_processor(update, context):
    query = update.callback_query
    print("choice_processor")
    if int(query['data']) == NDFL:
        return info_sheet_ndfl(update, context)
    elif int(query['data']) == FREEFORM:
        return info_sheet_freeform(update, context)
    elif int(query['data']) == SIMPLE:
        return info_sheet_simple(update, context)
    elif int(query['data']) == VISA:
        return info_sheet_visa(update, context)

def info_sheet_ndfl(update, context):
    update.message.reply_text("Укажите период, за который нужна справка")
    print("info_sheet_ndfl")
    return GET_PERIOD_OF_INFO_SHEET

def info_sheet_freeform(update, context):
    update.message.reply_text("Укажите период, за который нужна справка")
    print("info_sheet_freeform")
    return GET_PERIOD_OF_INFO_SHEET

def info_sheet_simple(update, context):
    print("info_sheet_simple")
    update.message.reply_text("Введите ФИО полностью")
    return DOCUMENTS_AMOUNT_SHOW_MESSAGE

def info_sheet_visa(update, context):
    print("info_sheet_visa")
    update.message.reply_text("Введите ФИО полностью")
    return DOCUMENTS_AMOUNT_SHOW_MESSAGE

def get_period_of_info_sheet(update, context):
    update.message.reply_text('На данный момент ваша завка: <...>')
    print("GET_PERIOD_OF_INFO_SHEET")
    return DOCUMENTS_AMOUNT_SHOW_MESSAGE

#helpers
def help(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Добро пожаловать. Введите /start для запуска бота")


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def get_token():
    f = open('token_tg.txt', 'r')
    tmp = f.readline().strip()
    f.close()
    return tmp


token = get_token()

def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(token, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error)


    handler_start = CommandHandler("start", start)
    handler_authentification = MessageHandler(Filters.all, authentification)
    handler_new_user = MessageHandler(Filters.all, new_user)
    handler_get_HR_contacts = CallbackQueryHandler(get_HR_contacts, pattern=str(GET_HR_CONTACTS))
    handler_get_document_copy_option = CallbackQueryHandler(get_document_copy_option, pattern=str(GET_DOCUMENT_COPY))
    handler_set_documents_amount = MessageHandler(Filters.all, set_documents_amount)
    handler_get_location =  CallbackQueryHandler(get_location)
    handler_final_words =  CallbackQueryHandler(final_words)

    handler_restart_order = CallbackQueryHandler(restart_order)

    handler_get_info_sheet_all_options = CallbackQueryHandler(get_info_sheet_all_options, pattern=str(GET_INFO_SHEET))
    handler_choice_processor = CallbackQueryHandler(choice_processor)

    handler_change_personal_info = CallbackQueryHandler(change_personal_info_options, pattern=str(CHANGE_PERSONAL_INFORMATION))
    handler_save_pi_to_change = CallbackQueryHandler(save_pi_to_change, pattern=r'^pi_\d+?\w+?')
    handler_get_new_pi_to_db = MessageHandler(Filters.all, change_personal_info_to_db)

    handler_info_sheet_ndfl = MessageHandler(Filters.all, info_sheet_ndfl)
    handler_info_sheet_freeform = MessageHandler(Filters.all, info_sheet_freeform)
    handler_info_sheet_simple = MessageHandler(Filters.all, info_sheet_simple)
    handler_info_sheet_visa = MessageHandler(Filters.all, info_sheet_visa)

    handler_get_period_of_info_sheet = MessageHandler(Filters.all, get_period_of_info_sheet)


    conv_handler = ConversationHandler(
        entry_points=[handler_start],
        #возможные состояния диалога
        states={
            #пользователь выбирает
            AUTHENTIFICATION : [handler_authentification],
            #обрабытываем сообшения пользователя
            AS_USER : [handler_get_HR_contacts, handler_get_document_copy_option, handler_get_info_sheet_all_options, handler_change_personal_info],
            DOCUMENTS_AMOUNT_SET_BY_USER : [handler_set_documents_amount],
            GET_LOCATION : [handler_get_location],
            FINAL_WORDS : [handler_final_words],
            GET_PERIOD_OF_INFO_SHEET : [handler_get_period_of_info_sheet],
            GET_INFO_SHEET : [handler_info_sheet_ndfl, handler_info_sheet_freeform, handler_info_sheet_simple, handler_info_sheet_visa],
            CHOICE_PROCESSOR : [handler_choice_processor],
            NEW_USER : [handler_new_user],
            SAVE_PI_TO_CHANGE : [handler_save_pi_to_change],
            NEW_PI_TO_DB : [handler_get_new_pi_to_db],
            RESTART_ORDER : [handler_restart_order]

        },
        fallbacks=[handler_start]
        #обрабатываем команды неизвестные и не понятные
        )
    updater.dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()


    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
