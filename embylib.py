
import requests
import json
from datetime import datetime
import dateutil.parser as parser
import urllib3

urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

HEADER = 'Emby UserId="", Client="Python", Device="Backup Script Manuvaldi", DeviceId="0001", Version="1.0.0.0"'
LIMIT = 10000

def authenticate_token(username=None, password=None, server=None, protohttps=False):

    if (protohttps==False):
        proto = "http://"
    else:
        proto = "https://"
    url = proto + server + '/emby/Users/AuthenticateByName'
    auth_header = {'X-Emby-Authorization' : HEADER, 'Content-Type': 'application/json'}
    auth_json = { "Username": username, "Password": password, "Pw": password }

    auth = requests.post(url, headers = auth_header, json = auth_json, verify=False )
    # print("Auth Code : " + str(auth.status_code))
    return({ "userid": auth.json()['User']['Id'],
             "token": auth.json()['AccessToken'],
             "server": proto + server,
             "sessionid": auth.json()["SessionInfo"]["Id"] })



def find_by_provider(api, provider):

    path = '/Users/' + api["userid"] + '/Items'
    print("Buscando " + provider)
    data_json = { "AnyProviderIdEquals": provider }

    results = _query(api=api, path=path, data=data_json)

    return(results)



def get_all_items(api):

    url = "%s/emby/Users/%s/Items" % (api["server"] , api["userid"])
    data_json = {   "api_key": api["token"],
                    "Recursive": True,
                    "Fields": "ProviderIds,ShareLevel",
                    "SortBy": "DateCreated,SortName,Type,Id",
                    "SortOrder": "Ascending",
                    "IncludeItemTypes": "Movie,Episode,Series",
                    "EnableUserData": True,
                    "EnableImages": False
                     }

    results={}
    results["Items"]=[]
    startindex = 0
    totales = 1
    print("   * Limit: " + str(LIMIT))
    while (startindex < totales):
        data_json.update({ "StartIndex": startindex, "Limit": LIMIT })
        results_tmp = requests.get(url,  params = data_json, verify=False ).json()
        results["Items"].extend(results_tmp["Items"])

        totales = results_tmp["TotalRecordCount"]
        startindex += len(results_tmp["Items"])

        print("   * Loading " + str(startindex) + '/' + str(totales))

    return(results)

def emby_get_item(api,id):

    url = "%s/emby/Users/%s/Items/%s" % (api["server"] , api["userid"], id)
    data_json = {   "api_key": api["token"] }

    result = requests.get(url,  params = data_json, verify=False ).json()

    return(result)


def update_item(api, id, type=None, data=None):

    auth_header = {'X-Emby-Authorization' : HEADER + ',Token="'+ api["token"] + '"', 'Content-Type': 'application/json' }
    data_json = {}

    if type == "Played":
        url = "%s/emby/Users/%s/PlayedItems/%s" % (api["server"] , api["userid"], id)
        if data is not None:
            # Data must be an timestamp str
            data_json = { "DatePlayed": datetime.fromtimestamp(int(data)).strftime("%Y%m%d%H%M%S") }
        results = requests.post(url, headers=auth_header, params=data_json, verify=False )
        if results.status_code == 200:
            print("   * Updated Item %s (%s)" % (id,type) )

    elif type == "Favorite":
        url = "%s/emby/Users/%s/FavoriteItems/%s" % (api["server"] , api["userid"], id)
        results = requests.post(url, headers=auth_header, params=data_json, verify=False )
        if results.status_code == 200:
            print("   * Updated Item %s (%s)" % (id,type) )

    elif type == "Playing":
        url = "%s/emby/Users/%s/PlayingItems/%s" % (api["server"] , api["userid"], id)
        data_json = { "PositionTicks" : data }
        results = requests.delete(url, headers=auth_header, params=data_json, verify=False )
        if results.status_code in [200,204]:
            print("   * Updated Item %s (%s)" % (id,type) )

    elif type == "UnPlayed":
        url = "%s/emby/Users/%s/PlayedItems/%s" % (api["server"] , api["userid"], id)
        results = requests.delete(url, headers=auth_header, verify=False )
        if results.status_code in [200,204]:
            print("   * Unplayed Item %s (%s)" % (id,type) )

    elif type == "UnFavorite":
        url = "%s/emby/Users/%s/FavoriteItems/%s" % (api["server"] , api["userid"], id)
        results = requests.delete(url, headers=auth_header, verify=False )
        if results.status_code in [200,204]:
            print("   * UnFavorite Item %s (%s)" % (id,type) )


    return(results)



def printp(jsonobject):
    print(json.dumps(jsonobject, indent=2))


def item_in_items(item, embyitems):

    matchitem = None
    for embyitem in embyitems["Items"]:
        if embyitem["Type"] == item["Type"]:
            if "Tmdb" in embyitem["ProviderIds"].keys() and "Tmdb" in item["ProviderIds"].keys():
                if embyitem["ProviderIds"]["Tmdb"] == item["ProviderIds"]["Tmdb"]:
                    matchitem = embyitem
                else:
                    matchitem = None
                    continue
            if "Imdb" in embyitem["ProviderIds"].keys() and "Imdb" in item["ProviderIds"].keys():
                if embyitem["ProviderIds"]["Imdb"] == item["ProviderIds"]["Imdb"]:
                    matchitem = embyitem
                else:
                    matchitem = None
                    continue
            if "Tvdb" in embyitem["ProviderIds"].keys() and "Tvdb" in item["ProviderIds"].keys():
                if embyitem["ProviderIds"]["Tvdb"] == item["ProviderIds"]["Tvdb"]:
                    matchitem = embyitem
                else:
                    matchitem = None
                    continue

            if matchitem is not None:
                return(matchitem)

    return(None)



def strproviders(item):

    output = ""
    if "ProviderIds" in item.keys():
        for provider in item["ProviderIds"].keys():
            if provider.lower() in ["tmdb", "tvdb", "imdb", "tvrage", "zap2it"]:
                output = output + provider + ":" + item["ProviderIds"][provider] + ", "

    return output[:-2]



def sync(src_items, src_api, dest_items, dest_api):

    for srcitem in src_items['Items']:

        # Played and Playing
        if srcitem["UserData"]["Played"] == True or srcitem["UserData"]["PlaybackPositionTicks"] > 0:
            destitem = item_in_items(srcitem, dest_items)
            if destitem == None:
                continue
            # Get item again to bring UserData: LastPlayedDate and more.
            srcitem = emby_get_item(src_api, srcitem['Id'])
            if 'LastPlayedDate' in srcitem['UserData'].keys():
                srcitemdate = datetime.timestamp(parser.parse(srcitem['UserData']['LastPlayedDate']))
            else:
                srcitemdate = 0

            destitem = emby_get_item(dest_api, destitem['Id'])
            if 'LastPlayedDate' in destitem['UserData'].keys():
                destitemdate = datetime.timestamp(parser.parse(destitem['UserData']['LastPlayedDate']))
            else:
                destitemdate = 0

            if srcitemdate > (destitemdate + 10800):

                print("   * EmbySrc Played: " + srcitem["Name"] + " ["+srcitem['Id']+"] " + " (" + strproviders(srcitem) + ") (" + str(srcitemdate) + ">" + str(destitemdate) + ")" )
                print("     - Found: " + destitem["Name"] + " ["+destitem['Id']+"] " + " (" + strproviders(destitem) +") watched at " + str(destitemdate))

                if srcitem["UserData"]["PlaybackPositionTicks"] == 0:
                    update_item(dest_api, destitem["Id"], "Played", srcitemdate)
                else:
                    update_item(dest_api, destitem["Id"], "Played", srcitemdate)
                    update_item(dest_api, destitem["Id"], "Playing", int(srcitem["UserData"]["PlaybackPositionTicks"]))

            elif destitem['UserData']["Played"] == False:
                print("   * PlexPlayed: " + srcitem["Name"] + " (" + strproviders(srcitem) +") (Only played state)" )
                print("     - Found: " + destitem["Name"] + " ["+destitem['Id']+"] " + " (" + strproviders(destitem) +") ")
                update_item(dest_api, destitem["Id"], "Played")

        # Favorites
        if srcitem["UserData"]["IsFavorite"] == True:
            destitem = item_in_items(srcitem, dest_items)
            if destitem is not None and destitem["UserData"]["IsFavorite"] == False:
                print("   * Favorite: " + srcitem["Name"])
                print("     - Found: " + destitem["Name"] + " (" + destitem["Id"] +")")
                update_item(dest_api, destitem["Id"], "Favorite")



def logout(api):

    auth_header = {'X-Emby-Authorization' : HEADER + ',Token="'+ api["token"] + '"', 'Content-Type': 'application/json' }
    data_json = {}
    url = "%s/emby/Sessions/Logout" % api["server"]
    result = requests.post(url, headers=auth_header, verify=False)


    if result.status_code in (200,204) :
        print(" * Logout: %s (%s)" % (api["server"], api["sessionid"]))
    else:
        print(auth_header)
        print(result.status_code)
        print(result.url)
        print(result.text)
        print(" * ERROR logout " + api["sessionid"])
