from lib.Utilities import get_hash


def authenticate_user(usr_id, passwd):
    f = open('lib/users', 'r')
    data = f.readlines()
    f.close()
    data = [i.strip() for i in data]
    if get_hash(usr_id + passwd + 'customer') in data:
        return 0
    elif get_hash(usr_id + passwd + 'seller') in data:
        return 1
    return -1


def add_user(usr_id, passwd, usertype='customer'):
    f = open('lib/users', 'a')
    f.writelines([get_hash(usr_id + passwd + usertype), "\n"])
    f.close()
