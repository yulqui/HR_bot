import pymongo
import sqlalchemy

from bson.objectid import ObjectId
from pymongo import MongoClient
client = MongoClient()
db = client.hrbot
collection_users = db.users
collection_unfilled_orders = db.unfilled_orders
collection_inprocess_orders = db.in_process_orders
collection_loc = db.locations
collection_dialogue = db.dialogue_tree

DB_KEY_USER_ID = 'user_id'
DB_LOC_ID = 'uid'

def get_last_order(user_id):
    res = collection_unfilled_orders.find_one({DB_KEY_USER_ID:user_id})
    if res != None:
        return res
    else:
        order = {DB_KEY_USER_ID: user_id,
            'order_step_id': 1,
            'order_fields': {}
            }
        collection_users.insert_one(order)
        return order

def get_info_dialogue_step(step_id):
    res = collection_dialogue.find_one({'id': step_id})
    return res

def insert_answr_order(user_id, answer):
    res = get_last_order(user_id)
    current_step_info = get_info_dialogue_step(res['order_step_id'])
    if current_step_info == None:
        raise CurrentStepError('Error step for user {0}'.format(user_id), 'Возникла ошибка. Просим заполнить запрос заново.' )
    anticipating = current_step_info['set_anticipated_field']
    if len(set(current_step_info[filled]) - set(res['order_fields'].keys())) == 0:
        insert_user_answer(user_id, anticipating, answer, order=res)
    else:
        pass #exception
    if type(current_step_info['next']) == dict:
        if answer in current_step_info['next'] and type(current_step_info['next'][answer]) == str:
            next_id = current_step_info['next'][answer]
        else:
            pass #exception
    elif type(current_step_info['next']) == str:
        next_id = current_step_info['next']
    else:
        raise Bot_Exception()

    update_order_step(user_id, next_id, order=res)



def update_order_step(user_id, next_id, order=None):
    if order == None:
        res = collection_unfilled_orders.find_one({DB_KEY_USER_ID: user_id})
    else:
        res=order
    collection_unfilled_orders.update_one({DB_KEY_USER_ID: user_id}, {'$set': {'order_step_id': next_id}})

def insert_user_answer(user_id, anticipated_info, answer, order=None):
    if order == None:
        res = collection_unfilled_orders.find_one({DB_KEY_USER_ID: user_id})
    else:
        res=order
    filled_fields = res['order_fields']
    filled_fields[anticipated_info] = answer
    collection_unfilled_orders.update_one({DB_KEY_USER_ID: user_id}, {'$set': {'order_fields': filled_fields}})


def check_user(user_id, key_list):
    search = collection_users.find_one({DB_KEY_USER_ID: user_id})
    keys_list = set(key_list) #преобразование кортежа во множество
    keys_search = set(search.keys())
    print( 'check user', keys_list.issubset(keys_search))
    return keys_list.issubset(keys_search)

def get_anticipated_info(user_id):
    search = collection_users.find_one({DB_KEY_USER_ID: user_id})
    if 'anticipated_info' in search:
        return search['anticipated_info']
    else:
        return None

def set_anticipated_info(user_id, key_info):
    collection_users.update_one({DB_KEY_USER_ID: user_id}, {'$set': {'anticipated_info': key_info}})

def missing_keys(user_id, key_list):
    search = collection_users.find_one({DB_KEY_USER_ID: user_id})
    keys_list = set(key_list)
    keys_search = set(search.keys())
    print('missing keys', keys_list.difference(keys_search))
    return list(keys_list.difference(keys_search))

def get_user_data_to_db(key, value, user_id):
    print('get user data to db: {0}, {1}:{2}'.format(user_id, key, value))
    collection_users.update_one({DB_KEY_USER_ID: user_id}, {'$set': {key: value}})

def show_personal_info(user_id):
    search = collection_users.find_one({DB_KEY_USER_ID: user_id})
    f = search['pi_1family_name']
    n = search['pi_2personal_name']
    o = search['pi_3fathers_name']
    t = search['pi_4phone']
    return f, n, o, t

def delete_order_by_user_id(user_id):
    collection_unfilled_orders.remove({DB_KEY_USER_ID:user_id})

def create_new_user(user_id):
    if collection_users.find_one({DB_KEY_USER_ID:user_id}) == None:
        result = collection_users.insert_one({DB_KEY_USER_ID:user_id})
        print(result.inserted_id)

def set_document_copy_to_db(user_id):
    collection_unfilled_orders.insert_one({DB_KEY_USER_ID:user_id, 'type_document':'copy'})

def set_documents_amount_to_db(user_id, amount):
    collection_unfilled_orders.update_one({DB_KEY_USER_ID: user_id}, {'$set': {'amount': amount}})

def set_info_sheet_to_db(user_id):
    collection_unfilled_orders.insert_one({DB_KEY_USER_ID:user_id, 'type_document':'info_sheet'})

def show_order_info(user_id):
    search = collection_unfilled_orders.find_one({DB_KEY_USER_ID: user_id})
    type = search['type_document']
    amount = search['amount']
    if 'subtype_document' in search:
        subtype = search['subtype_document']
    else:
        subtype = 'NA'
    if 'period'in search:
        period = search['period']
    else:
        period = 'NA'
    return type, amount, subtype, period

def set_location_to_db(user_id,  loc_name):
    collection_unfilled_orders.update_one({DB_KEY_USER_ID: user_id}, {'$set': {'location': loc_name}})

def get_loc_by_id(uid):
    location = collection_loc.find_one({DB_LOC_ID : uid})
    return location

def transfer_order_to_inprocess(user_id):
    col_source = collection_unfilled_orders
    col_target = collection_inprocess_orders
    #copy data from unfilled orders to inprocess orders
    # indexes from source_Collection will not copied in target_Collection
    col_source.aggregate([ {'$match': {DB_KEY_USER_ID:user_id} }, {'$out': str(col_target) } ])
    #remove data from unfilled orders
    col_source.remove({DB_KEY_USER_ID:user_id})
