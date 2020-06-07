import pymongo
import pprint
import hashlib
import datetime

#
# Either read directly from system.users or setup an audit log
#

# constants
SCRAM_SHA256 = 'SCRAM-SHA-256'
SCRAM_SHA1 = 'SCRAM-SHA-1'


def init_db():
    global client, dbadmin, coll_admin_users, db_password_tracker, coll_tracker_history
    client = pymongo.MongoClient('localhost', 27017)
    db_admin = client['admin']
    coll_admin_users = db_admin['system.users']
    db_password_tracker = client['password_tracker']
    coll_tracker_history = db_password_tracker['password_history']


def grab_credentials_for_user(user_obj):
    credentials = user_obj['credentials']
    hash_algorithm_key = None
    if SCRAM_SHA256 in credentials:
        hash_algorithm_key = SCRAM_SHA256
    if SCRAM_SHA1 in credentials:
        hash_algorithm_key = SCRAM_SHA1
    salt = credentials[hash_algorithm_key]['salt']
    server_key = credentials[hash_algorithm_key]['serverKey']
    stored_key = credentials[hash_algorithm_key]['storedKey']
    ret_obj = {
        'salt': salt,
        'server_key': server_key,
        'stored_key': stored_key
    }
    return ret_obj


def do_work():
    sample_user_obj_cur = coll_admin_users.find()
    for sample_user_obj in sample_user_obj_cur:
        if sample_user_obj is not None:
            if 'credentials' in sample_user_obj:
                credential_object = grab_credentials_for_user(sample_user_obj)

                salt = credential_object['salt']
                server_key = credential_object['server_key']
                stored_key = credential_object['stored_key']

                hash_engine = hashlib.sha256()
                hash_engine.update( (salt + ":" + server_key + ":" + stored_key).encode('utf-8') )
                digested_string = hash_engine.hexdigest()

                search_history_user = {
                    '_id': sample_user_obj['_id'],
                    'history.0.digested': digested_string
                }
                result = coll_tracker_history.find(search_history_user)

                if result.count() == 0:
                    upsert_history_user_filter = {
                        '_id': sample_user_obj['_id'],
                    }
                    #TODO Slice the array to limit to a specific size
                    upsert_history_user_push = {
                        '$push': {
                            'history': {
                                '$each': [
                                    {
                                        'digested': digested_string,
                                        'when': datetime.datetime.today()
                                    }
                                ],
                                '$position': 0
                            }
                        }
                    }

                    coll_tracker_history.update_one(upsert_history_user_filter, upsert_history_user_push, upsert=True)


def main():
    init_db()
    do_work()


if __name__=='__main__':
    main()
