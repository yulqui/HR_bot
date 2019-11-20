#states
START = 1
AUTHENTIFICATION = 2
AS_ADMIN = 3
AS_USER = 4
GET_INFO_SHEET = 5
GET_DOCUMENT_COPY = 6
GET_HR_CONTACTS = 7
DOCUMENTS_AMOUNT_SET_BY_USER = 9
GET_LOCATION = 10
# SSHPB = 11
# OSHOG = 12
# SSHV =  13
# PRISMA = 14
FINAL_WORDS = 15
GET_PERIOD_OF_INFO_SHEET = 16
USER_OPTIONS_SHEET = 17
NDFL = 18
FREEFORM = 19
SIMPLE = 20
VISA = 21
CHOICE_PROCESSOR = 22
NEW_USER = 23
CHANGE_PERSONAL_INFORMATION = 24
SAVE_PI_TO_CHANGE = 25
NEW_PI_TO_DB = 26
CONTINUE_FILLING = 27
STOP_FILLING = 28
RESTART_ORDER = 29



dict_keys_decoder = {'pi_1family_name': 'Пожалуйста, укажите вашу фамилию:',
'pi_2personal_name': 'Пожалуйста, укажите ваше имя:',
'pi_3fathers_name': 'Пожалуйста, укажите ваше отчество. Если в вашем паспорте не указано отчество, то ответьте "нет":',
'pi_4phone': 'Пожалуйста, укажите ваш номер телефона для уточнения деталей заявки в случае возникновения вопросов:'}



def decode_keys_to_msg(key):
    print('key to message decoder')
    return dict_keys_decoder[key]
