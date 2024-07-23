# emby-sync-tools

Syncronization and backup tools for Emby Media Server. Sync favorites, played, and playing between 2 servers.

List of tools:

- `embysync.py`
- `embyexport.py`
- `embyimport.py`

## Sync servers (`embysync.py`)

This tool sync server 1 to server 2. Unidirectionally.

### How to run

```
python embysync.py \
 --url1 server1.example.com:8080 --https1 --username1 userone --password1 XXXXXXX \
 --url2 server2.example.com:8080 --https2 --username2 usertwo --password2 YYYYYYY
```

NOTE: Add `https1` and/or `https2` options to use https connection to servers.

## Export All items (`embyexport.py`)

Export from server to a json file

### How to run

```
python embyexport.py \
 --url server1.example.com:8080 --https --username userone --password XXXXXXX --backupfile backup.json
```

NOTE: Add `https` option to use https connection to servers.


## Import backup into server

Import watched and favorites from backup file

### How to run

```
python embyimport.py \
 --url server1.example.com:8080 --https --username userone --password XXXXXXX --backupfile backup.json
```

NOTE: Add `https` option to use https connection to servers.
