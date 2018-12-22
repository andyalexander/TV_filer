#!/usr/bin/env bash
python CopyFiles.py
#curl http://192.168.2.74:32400/library/sections/1/refresh?X-Plex-Token=px9JmF1FA5Gbkomc98D1
#curl http://192.168.2.74:32400/library/sections/2/refresh?X-Plex-Token=px9JmF1FA5Gbkomc98D1
curl http://127.0.0.1:32400/library/sections/1/refresh?X-Plex-Token=px9JmF1FA5Gbkomc98D1
curl http://127.0.0.1:32400/library/sections/2/refresh?X-Plex-Token=px9JmF1FA5Gbkomc98D1
