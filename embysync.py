import json
import sys
import getopt
from embylib import *




## Main

def main(argv):
    log_file = False
    https1 = False
    https2 = False
    username = None
    backup_path = ''

    try:
        opts, args = getopt.getopt(argv, "hl", ["help", "log",
                                                "url1=", "https1", "username1=", "password1=",
                                                "url2=", "https2", "username2=", "password2="])
    except getopt.GetoptError:
        print_debug(['embysync.py --url1 embyserver1:12345 --https1 --username1 useremby1 --password1 mypassword1 --url2 embyserver2:12345 --https2 --username2 useremby2 --password2 mypassword2 '])
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print_debug(['embysync.py --url1 embyserver1:12345 --https1 --username1 useremby1 --password1 mypassword1 --url2 embyserver2:12345 --https2 --username2 useremby2 --password2 mypassword2 '])
            sys.exit()
        # elif opt == '-l' or opt == '--log':
        #     log_file = True

        elif opt == '--url1':
            server_url1 = arg
        elif opt == "--https1":
            https1 = True
        elif opt == '--username1':
            server_username1 = arg
        elif opt == '--password1':
            server_password1 = arg

        elif opt == '--url2':
            server_url2 = arg
        elif opt == "--https2":
            https2 = True
        elif opt == '--username2':
            server_username2 = arg
        elif opt == '--password2':
            server_password2 = arg

    # Authentication
    api1 = authenticate_token(username=server_username1, password=server_password1, server=server_url1, protohttps=https1)
    print('User ID 1 : ' + api1["userid"])
    print('  Token 1 : ' + api1["token"])
    print(' Server 1 : ' + api1["server"])
    api2 = authenticate_token(username=server_username2, password=server_password2, server=server_url2, protohttps=https2)
    print('User ID 2 : ' + api2["userid"])
    print('  Token 2 : ' + api2["token"])
    print(' Server 2 : ' + api2["server"])

    print(" * Getting items from " + api1["server"])
    embyitems1 = get_all_items(api1)
    print("total: " + str(len(embyitems1["Items"])))

    print(" * Getting items from " + api2["server"])
    embyitems2 = get_all_items(api2)
    print("total: " + str(len(embyitems2["Items"])))


    print(" * Syncing items from " + api1["server"] + " -> " + api2["server"])
    sync(embyitems1, api1, embyitems2, api2)


    logout(api1)
    logout(api2)




if __name__ == "__main__":
    main(sys.argv[1:])
