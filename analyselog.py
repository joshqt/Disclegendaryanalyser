import requests
from math import ceil
import json

def getresults(reportid,playerid,starttime,endtime):
    legendarys = {132461: "Xalans",132444 :"Prydaz",144258: "Velens",132436: "Skjoldr"}
    traits ={197708:0,197729:0,197715:0,238063:0}
    apikey = "62daacc500c75b1d73519188338c166b"
    fight = requests.get("https://www.warcraftlogs.com:443/v1/report/fights/" + reportid + "?api_key=" + apikey)
    people = {}
    for x in fight.json()["friendlies"]:
        people[x["id"]] = x["name"]
    newtimestamp = str(starttime)

    atonementdmgtakentable = requests.get(
        "https://www.warcraftlogs.com:443/v1/report/tables/damage-taken/" + reportid + "?start=" + starttime + "&end=" + endtime + "&filter=%28in%20range%20from%20type%20%3D%20%22applybuff%22%20and%20ability.name%20%3D%20%22Atonement%22%20to%20type%20%3D%20%22removebuff%22%20and%20ability.name%20%3D%20%22Atonement%22%20group%20by%20target%20on%20target%20end%29%20and%20%28type%20%3D%20%22damage%22%20and%20target.type%20%3D%20%22Player%22%29&translate=true&api_key=" + apikey)
    atonementdamagetaken = 0
    for x in atonementdmgtakentable.json()["entries"]:
        atonementdamagetaken += x["total"]


    barrierhealingtable = requests.get("https://www.warcraftlogs.com:443/v1/report/tables/healing/"+reportid+"?start="+starttime+"&end="+endtime+"&sourceid="+playerid+"&filter=%28in%20range%20from%20type%20%3D%20%22applybuff%22%20and%20ability.name%20%3D%20%22Power%20Word%3A%20Barrier%22%20to%20type%20%3D%20%22removebuff%22%20and%20ability.name%20%3D%20%22Power%20Word%3A%20Barrier%22%20group%20by%20target%20on%20target%20end%29%20and%20%28inCategory%28%22healing%22%29%20%3D%20true%20and%20target.type%20%3D%20%22Player%22%29&translate=true&api_key="+apikey)
    barrierhealing = 0
    for x in barrierhealingtable.json()["entries"]:
        if x["name"] == "Atonement":
            barrierhealing += round(x["total"]/2)
    nerohealing = 0
    neroquery = requests.get(
        "https://www.warcraftlogs.com:443/v1/report/tables/healing/" + reportid + "?start=" + starttime + "&end=" + endtime + "&sourceid=" + playerid + "&filter=%28not%20in%20range%20from%20type%20%3D%20%22applybuff%22%20and%20ability.name%20%3D%20%22Atonement%22%20to%20type%20%3D%20%22removebuff%22%20and%20ability.name%20%3D%20%22Atonement%22%20group%20by%20target%20on%20target%20end%29%20and%20%28inCategory%28%22healing%22%29%20%3D%20true%20and%20target.type%20%3D%20%22Player%22%29%20and%20%28in%20range%20from%20type%20%3D%20%22applybuff%22%20and%20ability.name%20%3D%20%22Power%20Word%3A%20Barrier%22%20to%20type%20%3D%20%22removebuff%22%20and%20ability.name%20%3D%20%22Power%20Word%3A%20Barrier%22%20group%20by%20target%20on%20target%20end%29%20&translate=true&api_key=" + apikey)
    for x in neroquery.json()["entries"]:
        if x["name"] == "Atonement":
            for y in x["subentries"]:
                if y["name"] == "Penance":
                    nerohealing = (y["total"])

    output = []
    while int(newtimestamp) < int(endtime):
        try:
            eventsgrab = requests.get(
                "https://www.warcraftlogs.com:443/v1/report/events/" + reportid + "?start=" + newtimestamp + "&end=" + endtime + "&actorid=" + playerid + "&translate=true&api_key=" + apikey)
            output += eventsgrab.json()["events"]
            newtimestamp = str(eventsgrab.json()["nextPageTimestamp"])
            print("collected to " + newtimestamp)
        except:
            break

    legendarys = []
    hasdrape = False
    for x in output[0]["gear"]:
        if x["id"] == 142170:
            hasdrape = True
        if x["quality"] == 5:
            legendarys.append(x["id"])
    print(people[int(playerid)], "has", legendarys, "legendarys")

    for x in output[0]["artifact"]:
        if x["spellID"] in traits:
            traits[x["spellID"]] = x["rank"]
    print(traits)

    leniencevalue = round((atonementdamagetaken * (100 / (100 - (0.5 * traits[238063])))) - atonementdamagetaken)

    totalhealing = 0
    prydazhealing = 0
    skjoldrhealing = 0
    healingtable = requests.get(
        "https://www.warcraftlogs.com:443/v1/report/tables/healing/" + reportid + "?start=" + starttime + "&end=" + endtime + "&sourceid=" + playerid + "&translate=true&api_key=" + apikey)

    for x in healingtable.json()["entries"]:
        #  print (x,"\n")
        if 132436 in legendarys:
            if x["name"] == "Power Word: Shield":
                skjoldrhealing += x["total"] - x["total"] / 1.15
        if x["name"] == "Xavaric's Magnum Opus":
            prydazhealing = x["total"]

        if x["name"] == "Atonement":
            for x in x["subentries"]:
                totalhealing += x["total"]
        else:
            totalhealing += x["total"]
    round(skjoldrhealing)
    xalanstotal = 0

    contritiontotal = 0
    contdict = {x: [0, 0] for x in people}
    for x in output:
        try:
            if (x["type"] == "applybuff" or x["type"] == "refreshbuff") and x["ability"]["name"] == "Atonement":
                contdict[x["targetID"]] = [int(x["timestamp"]) + 15000, int(x["timestamp"]) + 18000]
            # print (contdict)
            if (x["type"] == "heal") and x["ability"]["name"] == "Atonement" and x["timestamp"] > contdict[x["targetID"]][
                0] and x["timestamp"] < contdict[x["targetID"]][1]:
                contritiontotal += x["amount"]
        except:
            pass
    contritionpercent = round(contritiontotal / totalhealing * 100,2)

    xalanshealing = 0
    newtime = int(starttime) + 17000
    if 132461 in legendarys:
        for x in output:
            if (x["type"] == "applybuff" or x["type"] == "refreshbuff") and x["ability"]["name"] == "Atonement" and x[
                "targetID"] == int(playerid):
                newtime = int(x["timestamp"]) + 18000
            if (x["type"] == "heal") and x["ability"]["name"] == "Atonement" and x["targetID"] == int(playerid) and x[
                "timestamp"] > newtime:
                xalanshealing += x["amount"]
    xalanspercent = round(xalanshealing/totalhealing*100,2)
    prydazpercent = round(prydazhealing/totalhealing*100,2)
    skjoldrpercent = round(skjoldrhealing / totalhealing * 100, 2)
    neropercent = round(nerohealing / totalhealing * 100, 2)
    casts = requests.get(
        "https://www.warcraftlogs.com:443/v1/report/tables/casts/" + reportid + "?start=" + starttime + "&end=" + endtime + "&sourceid=" + playerid + "&translate=true&api_key=" + apikey)
    totalcasts = 0
    approvedspells = ['Plea', 'Power Word: Radiance', 'Smite', 'Power Word: Shield', 'Penance', 'Purge the Wicked',
                      "Power Word: Solace"
        , 'Halo', 'Shadow Mend', "Divine Star", "Clarity of Will", "Shadow Word: Pain"]

    for x in casts.json()["entries"]:
        if x["name"] in approvedspells:
            if x["name"] == "Penance":
                totalcasts += ceil(x["total"] / 4)
            else:
                totalcasts += x["total"]
    manaadjustedcasts = round(totalcasts / (((output[-1]["timestamp"] - int(starttime)) / 1000) / 60),2)

    return [manaadjustedcasts,
            "{:,}".format(leniencevalue),
            "{:,}".format(barrierhealing),
            "{:,}".format(contritiontotal),
            contritionpercent,
            "{:,}".format(xalanshealing),
            xalanspercent,
            "{:,}".format(prydazhealing),
            prydazpercent,
            "{:,}".format(skjoldrhealing),
            skjoldrpercent,
            "{:,}".format(nerohealing),
            neropercent]






  #                                                 "{:,}".format(nerohealing)+ str(nerohealing / totalhealing * 100)+ "% Of your healing was from nero"]
