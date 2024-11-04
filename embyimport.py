import json
import sys
import getopt
from  embylib import *

## Main
def main(argv):
    log_file = False
    https = False
    username = None
    backup_path = ''

    try:
        opts, args = getopt.getopt(argv, "hl", ["help", "log",
                                                "backupfile=",
                                                "url=", "https", "username=", "password="])
    except getopt.GetoptError:
        print_debug(['embyimport.py --url embyserver:12345 --https --username useremby --password mypassword --backupfile backupfile'])
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print_debug(['embyimport.py --url embyserver:12345 --https --username useremby --password mypassword --backupfile backupfile'])
            sys.exit()
        # elif opt == '-l' or opt == '--log':
        #     log_file = True
        elif opt == "--https":
            https = True
        elif opt == '--backupfile':
            backupfile = arg
        elif opt == '--url':
            server_url = arg
        elif opt == '--username':
            server_username = arg
        elif opt == '--password':
            server_password = arg


    # Load json file JSON file
    print(" * Loading items from Backup " + backupfile)
    f = open(backupfile)
    jsonitems = json.load(f)
    f.close()


    # Authentication
    api = authenticate_token(username=server_username, password=server_password, server=server_url, protohttps=https, verify=False)


    print('User ID : ' + api["userid"])
    print('  Token : ' + api["token"])
    print(' Server : ' + api["server"])

    print(" * Getting items from Emby " + api["server"])
    embyitems = get_all_items(api)


    print("total: " + str(len(embyitems["Items"])))
    for item in jsonitems['Items']:
        if item["UserData"]["Played"] == True:
            embyitem = item_in_items(item, embyitems)
            if embyitem is not None and embyitem["UserData"]["Played"] == False:
                print(" - " + item["Name"])
                print("   - Found: " + embyitem["Name"] + " (" + embyitem["Id"] +") " + " (" + embyitem["Id"] +")")
                update_item(api, embyitem["Id"], "Played")

        if item["UserData"]["IsFavorite"] == True:
            embyitem = item_in_items(item, embyitems)
            if embyitem is not None and embyitem["UserData"]["IsFavorite"] == False:
                print(" - " + item["Name"])
                print("   - Found: " + embyitem["Name"] + " (" + embyitem["Id"] +") " + " (" + embyitem["Id"] +")")
                update_item(api, embyitem["Id"], "Favorite")

    logout(api)



if __name__ == "__main__":
    main(sys.argv[1:])

# Closing file
