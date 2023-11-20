
import requests
import json
from datetime import datetime
import dateutil.parser as parser
from plexapi.server import PlexServer
from plexapi.myplex import MyPlexAccount

HEADER = 'Emby UserId="", Client="Android", Device="Samsung Galaxy SIII", DeviceId="xxx3", Version="1.0.0.0"'
LIMIT = 10000

def authenticate_token(username=None, password=None, server=None):

    url = 'http://' + server + '/emby/Users/AuthenticateByName'
    auth_header = {'X-Emby-Authorization' : HEADER, 'Content-Type': 'application/json'}
    auth_json = { "Username": username, "Password": password, "Pw": password }

    auth = requests.post(url, headers = auth_header, json = auth_json )
    # print("Auth Code : " + str(auth.status_code))
    return({ "userid": auth.json()['User']['Id'],
             "token": auth.json()['AccessToken'],
             "server": server,
             "sessionid": auth.json()["SessionInfo"]["Id"] })




def find_by_provider(api, provider):

    path = '/Users/' + api["userid"] + '/Items'
    print("Buscando " + provider)
    data_json = { "AnyProviderIdEquals": provider }

    results = _query(api=api, path=path, data=data_json)

    return(results)



def get_all_items(api):

    url = "http://%s/emby/Users/%s/Items" % (api["server"] , api["userid"])
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
        results_tmp = requests.get(url,  params = data_json ).json()
        results["Items"].extend(results_tmp["Items"])

        totales = results_tmp["TotalRecordCount"]
        startindex += len(results_tmp["Items"])

        print("   * Loading " + str(startindex) + '/' + str(totales))

    return(results)

def emby_get_item(api,id):

    url = "http://%s/emby/Users/%s/Items/%s" % (api["server"] , api["userid"], id)
    data_json = {   "api_key": api["token"] }

    result = requests.get(url,  params = data_json ).json()
    # results={}
    # results["Items"]=[]
    # startindex = 0
    # totales = 1
    # print("   * Limit: " + str(LIMIT))
    # while (startindex < totales):
    #     data_json.update({ "StartIndex": startindex, "Limit": LIMIT })
    #     results_tmp = requests.get(url,  params = data_json ).json()
    #     results["Items"].extend(results_tmp["Items"])
    #
    #     totales = results_tmp["TotalRecordCount"]
    #     startindex += len(results_tmp["Items"])
    #
    #     print("   * Loading " + str(startindex) + '/' + str(totales))

    return(result)


def update_item(api, id, type=None, data=None):

    auth_header = {'X-Emby-Authorization' : HEADER + ',Token="'+ api["token"] + '"', 'Content-Type': 'application/json' }
    data_json = {}

    if type == "Played":
        url = "http://%s/emby/Users/%s/PlayedItems/%s" % (api["server"] , api["userid"], id)
        if data is not None:
            # Data must be an timestamp str
            data_json = { "DatePlayed": datetime.fromtimestamp(int(data)).strftime("%Y%m%d%H%M%S") }

    elif type == "Favorite":
        url = "http://%s/emby/Users/%s/FavoriteItems/%s" % (api["server"] , api["userid"], id)

    elif type == "Playing":
        # print(emby_get_item(api, id))
        # update_item(api,id,"Played,da")
        url = "http://%s/emby/Users/%s/PlayingItems/%s" % (api["server"] , api["userid"], id)
        # data_json = { "PositionTicks" : data, "MediaSourceId": 1, "NextMediaType": "Movie" }
        data_json = { "PositionTicks" : data }
        # print(data_json)
        results = requests.delete(url, headers=auth_header, params=data_json )
        # print(results.status_code)
        # print(results.url)
        # print(results.text)
        # print(results.reason)
        if results.status_code in [200,204]:
            print("   * Updated Item %s (%s)" % (id,type) )

    if type != "Playing":
        results = requests.post(url, headers=auth_header, params=data_json )
        if results.status_code == 200:
            print("   * Updated Item %s (%s)" % (id,type) )

        # print(results.status_code)
        # print(results.url)
        # print(results.text)

    return(results)



# def _to_lower(array):
#     out = map(lambda x:x.lower(), array)
#     output = list(out)
#     return(output)

def printp(jsonobject):
    print(json.dumps(jsonobject, indent=2))

def emby_get_item_by_provider_online(api,item):

        url = "http://%s/emby/Users/%s/Items" % (api["server"] , api["userid"])
        providers = ""
        for provtype in item["ProviderIds"]:
            providers += provtype.lower() + "." + item["ProviderIds"][provtype] + ","
        providers = providers[:-1]
        data_json = { "api_key": api["token"],
                    "AnyProviderIdEquals": providers,
                    "Recursive": True,
                    "Fields": "ProviderIds",
                    "SortBy": "DateCreated,SortName,Type,Id",
                    "SortOrder": "Ascending",
                    "IncludeItemTypes": "Movie,Episode,Series",
                    "EnableUserData": True,
                    "EnableImages": False }
        # print(data_json)
        result = requests.get(url,  params = data_json )
        # printp(result.json()["Items"])
        print("RESULTADOS: " + str(len(result.json()["Items"])) )
        if result.status_code == 200 and len(result.json()["Items"]) > 0:
            item = result.json()["Items"][0]
            # printp(item)
            extendeditem = emby_get_item(api,item['Id'])
            printp(extendeditem)
            return(extendeditem)
        else:
            # if provtype == "Tmdb":
            #     data_json = {   "api_key": api["token"], "AnyProviderIdEquals": "tmdb."+item["ProviderIds"]["Tmdb"] }
            #     print(data_json)
            #     result = requests.get(url,  params = data_json )
            #     print(result)
            #     if result.status_code == 200:
            #         return(result)
            # elif provtype == "Imdb":
            #     data_json = {   "api_key": api["token"], "AnyProviderIdEquals": "imdb."+item["ProviderIds"]["Imdb"] }
            #     print(data_json)
            #     result = requests.get(url,  params = data_json )
            #     print(result)
            #     if result.status_code == 200:
            #         return(result)
            # elif provtype == "Tvdb":
            #     data_json = {   "api_key": api["token"], , "AnyProviderIdEquals": "tvdb."+item["ProviderIds"]["Tvdb"] }
            #     print(data_json)
            #     result = requests.get(url,  params = data_json )
            #     print(result)
            #     if result.status_code == 200:
            #         return(result)
            return(None)

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
    # url = "http://%s/emby/Sessions/%s/Users/%s" % (api["server"] , api["sessionid"], api["userid"])
    # result = requests.delete(url, headers=auth_header)
    url = "http://%s/emby/Sessions/Logout" % api["server"]
    result = requests.post(url, headers=auth_header)


    if result.status_code in (200,204) :
        print(" * Logout: %s (%s)" % (api["server"], api["sessionid"]))
    else:
        print(auth_header)
        print(result.status_code)
        print(result.url)
        print(result.text)
        print(" * ERROR logout " + api["sessionid"])



def plex_authentication(baseurl, token):
    plexAccount = MyPlexAccount(token=token)
    return(plexAccount)


def plex_get_favorite_items(plexAccount):

    results={}
    results["Items"]=[]
    results["Raw"] = plexAccount.watchlist(maxresults=5000)
    for video in results["Raw"]:
        providers = {}
        for guid in video.guids:
            providers[guid.id.split(":")[0].lower().capitalize()] = guid.id.split("/")[2].lower()
        userstate = plexAccount.userState(video)
        # print(userstate.watchlistedAt)
        watchlistedat = datetime.timestamp(userstate.watchlistedAt) if userstate.watchlistedAt is not None else 0
        # print(watchlistedat)
        results["Items"].append({"Name": video.title, "Type": video.TYPE, "ProviderIds": providers, "watchlistedAt": watchlistedat})
        # results["Items"].append({"Name": video.title, "Type": video.TYPE, "ProviderIds": providers})
        # print(" * " + video.title + " (" + video.TYPE + ")")
    return(results)



def plex_get_watched_items(plexAccount):
    results={}
    results["Raw"]=[]
    results["Items"]=[]
    resources = plexAccount.resources()
    for resource in resources:
        print("   * Server: " + resource.name)
        connectionPlexServer = resource.connect()
        sections = connectionPlexServer.library.sections()
        print("     * Limit: " + str(LIMIT))

        for section in sections:
            print("     * Section: " + section.title )
            totalitems = 0

            for libtype in ['movie','show','episode']:
                startindex = 0
                lastcount = LIMIT
                while (lastcount == LIMIT):
                    try:
                        results_tmp = section.search(libtype=libtype, unwatched=False, container_start=startindex, limit=LIMIT)
                        results["Raw"].extend(results_tmp)
                        startindex += len(results_tmp)
                        lastcount = len(results_tmp)
                        print("       * Loading " + libtype + ": " + str(startindex) )

                    except Exception as err:
                        # print("Error buscando " + libtype)
                        lastcount = 0
                        # print(f"Unexpected {err=}, {type(err)=}")
                        # print("   * Loading " + libtype + ": 0")
                totalitems += startindex
            print("     * Loading Total " + str(totalitems) )

    for video in results["Raw"]:
        providers = {}

        for guid in video.guids:
            providers[guid.id.split(":")[0].lower().capitalize()] = guid.id.split("/")[2].lower()

        lastviewedat = datetime.timestamp(video.lastViewedAt) if video.lastViewedAt is not None else 0

        try:
            viewOffset = video.viewOffset
        except:
            viewOffset = 0

        jsondata={"Name": video.title, "Type": video.TYPE, "ProviderIds": providers, "lastViewedAt": lastviewedat , "viewOffset": viewOffset }
        # print(jsondata)
        results["Items"].append(jsondata)
        # print(" * " + video.title + " (" + video.TYPE + ")")

    return(results)



def sync_plex2emby(plex_watched,plex_favorite,embyitems, api):

    print(" ** Syncing Played items from Plex to Emby")
    for plexitem in plex_watched["Items"]:
        embyitem = item_in_items(plexitem, embyitems)
        if embyitem == None:
            continue

        # Get item again to bring UserData: LastPlayedDate and more.
        embyitem = emby_get_item(api,embyitem['Id'])

        if 'LastPlayedDate' in embyitem['UserData']:
            embyplayeddate = datetime.timestamp(parser.parse(embyitem['UserData']['LastPlayedDate']))
        else:
            embyplayeddate = 0

        # print(" * PlexPlayed: " + plexitem["Name"] + " (" + strproviders(plexitem) + ") (" + str(plexitem["lastViewedAt"]) + ">" + str(embyplayeddate) + ")" + ", Offset: "+ str(plexitem["viewOffset"]))
        if plexitem["lastViewedAt"] > embyplayeddate:

            print(" * PlexPlayed: " + plexitem["Name"] + " (" + strproviders(plexitem) + ") (" + str(plexitem["lastViewedAt"]) + ">" + str(embyplayeddate) + ")" )
            print("   - Found: " + embyitem["Name"] + " ["+embyitem['Id']+"] " + " (" + embyitem["Id"] +") " + " (" + strproviders(embyitem) +") watched at " + str(embyplayeddate))

            if plexitem["viewOffset"] == 0:
                update_item(api, embyitem["Id"], "Played", plexitem["lastViewedAt"])
            else:
                update_item(api, embyitem["Id"], "Playing", int(plexitem["viewOffset"]*10000))

        elif embyitem['UserData']["Played"] == False:
            print(" * PlexPlayed: " + plexitem["Name"] + " (" + strproviders(plexitem) +") (Only played state)" )
            print("   - Found: " + embyitem["Name"] + " ["+embyitem['Id']+"] " + " (" + strproviders(embyitem) +") ")
            update_item(api, embyitem["Id"], "Played")
        # else:
        #     # print("ticks: " + str(int(plexitem["viewOffset"]*10000)) + "<->" + str(embyitem["UserData"]["PlaybackPositionTicks"]) )
        #     if int(plexitem["viewOffset"]*10000) >= embyitem["UserData"]["PlaybackPositionTicks"]:
        #         print("lastviewed: " + str(plexitem["lastViewedAt"]))
        #         print(" * PlexPlaying: " + plexitem["Name"] + " (" + strproviders(plexitem) +") (" + str(int(plexitem["viewOffset"]*10000)) + "<->" + str(embyitem["UserData"]["PlaybackPositionTicks"]) + ")" )
        #         print("   - Found: " + embyitem["Name"] + " ["+embyitem['Id']+"] " + " (" + strproviders(embyitem) +") ")
        #         # print("current ticks: " + str(embyitem["UserData"]["PlaybackPositionTicks"]))
        #         # print("media source")
        #         # printp(embyitem["MediaSources"])
        #         update_item(api, embyitem["Id"], "Playing", int(plexitem["viewOffset"]*10000))

    print(" ** Syncing Watchlist/Favorite items from Plex to Emby")
    for plexitem in plex_favorite["Items"]:
        # print(" * PlexPlayed: " + plexitem["Name"] + " (" + strproviders(plexitem) +")")
        embyitem = item_in_items(plexitem, embyitems)
        if embyitem is not None and embyitem["UserData"]["IsFavorite"] == False:
            print(" * PlexWatchlist: " + plexitem["Name"] + " (" + strproviders(plexitem) +") WatchListed At " + str(plexitem["watchlistedAt"]))
            print("   - Found: " + embyitem["Name"] + " (" + embyitem["Id"] +") " + " (" + strproviders(embyitem) +") at" )
            print(embyitem["UserData"])
            update_item(api, embyitem["Id"], "Favorite")
