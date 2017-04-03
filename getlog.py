import requests
import json
from math import ceil


apikey = "62daacc500c75b1d73519188338c166b"


difficulty = {1:"LFR",2:"Flex",3:"Normal",4:"Heroic",5:"Mythic"}

def getpeople(reportid):
    fight = requests.get("https://www.warcraftlogs.com:443/v1/report/fights/" + reportid + "?api_key=" + apikey)
    if fight.status_code == 400:
        print ("here")
        raise ValueError (fight.json()["error"])
    else:
        priestsdict = {}
        fights = []
        fightsdict = {}
        for x in fight.json()["friendlies"]:
            if x["type"] == "Priest":
                priestsdict[x["name"]] = x["id"]
        for x in fight.json()["fights"]:
            if x["boss"]>0 and x["difficulty"] in difficulty:
                duration = "%02d:%02d" % (divmod((x["end_time"]-x["start_time"])/1000, 60))
                fightdifficulty = difficulty[x["difficulty"]]
                fightsdict[x["name"]+" "+fightdifficulty+" "+("Wipe","Kill")[x["kill"]]+" "+duration] = [x["start_time"],x["end_time"]]
                fights.append(x["name"]+" "+fightdifficulty+" "+("Wipe","Kill")[x["kill"]]+" "+duration)
        return (priestsdict,fights,fightsdict)


