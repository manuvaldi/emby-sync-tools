import json
import sys
import getopt
from  embylib import *



## Main
def main(argv):
    log_file = False
    username = None
    backup_path = ''

    try:
        opts, args = getopt.getopt(argv, "hl", ["help", "log",
                                                "backupfile=",
                                                "url=", "username=", "password="])
    except getopt.GetoptError:
        print_debug(['embyexport.py --url embyserver:12345 --username useremby --password mypassword --backupfile backupfile'])
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print_debug(['embyexport.py --url embyserver:12345 --username useremby --password mypassword --backupfile backupfile'])
            sys.exit()
        # elif opt == '-l' or opt == '--log':
        #     log_file = True
        elif opt == '--backupfile':
            backupfile = arg
        elif opt == '--url':
            server_url = arg
        elif opt == '--username':
            server_username = arg
        elif opt == '--password':
            server_password = arg


    # Authentication
    api = authenticate_token(username=server_username, password=server_password, server=server_url)
    print(' * User ID : ' + api["userid"])
    print(' * Token : ' + api["token"])
    print(' * Server : ' + api["server"])


    print(" * Getting items from Emby " + api["server"])
    embyitems = get_all_items(api)
    with open(backupfile, "w") as outfile:
        outfile.write(json.dumps(embyitems, indent=2))


    logout(api)



if __name__ == "__main__":
    main(sys.argv[1:])
