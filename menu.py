from states_bot import *
import states_bot

#[[{}, {}]]

main_menu_list = [
[{'text': "Заказать справку",
'value': GET_INFO_SHEET},
{'text': "Контакты HR",
'value': GET_HR_CONTACTS}],
[{'text': "Заказать копию трудовой книжки",
'value': GET_DOCUMENT_COPY},
{'text': 'Изменить персональные данные',
'value': CHANGE_PERSONAL_INFORMATION}]
]

filling_out_order_list = [
[{'text': 'Продолжить',
'value': CONTINUE_FILLING}],
[{'text': 'Заполнить заново',
'value': STOP_FILLING}]
]

keys_list = list(dict_keys_decoder.keys())

change_pi_menu_list = [
[{'text': 'Фамилию',
'value': keys_list[0]},
{'text': 'Имя',
'value': keys_list[1]}],
[{'text': 'Отчество',
'value': keys_list[2]},
{'text': 'Телефон',
'value': keys_list[3]}]
]

location_choice_list = [
[{'text': 'SSH Palace Bridge',
'value': states_bot.SSHPB},
{'text': 'OSH Olympia Garden',
'value': OSHOG}],
[{'text': 'SSH Vasilievsky',
'value': SSHV},
{'text': 'офис PRISMA, Большой пр. ВО, 68',
'value': PRISMA}]
]

info_sheet_options_list = [
[{'text': '2НДФЛ',
'value': NDFL},
{'text': 'в свободной форме о заработке за 3 месяца',
'value': FREEFORM}],
[{'text': 'подтверждение работы',
'value': SIMPLE},
{'text': 'для визы',
'value': VISA}]
]

order_finalization_list = [
[{'text': 'Да',
'value': FINAL_WORDS}],
[{'text': 'Нет',
'value': STOP_FILLING}]
]
