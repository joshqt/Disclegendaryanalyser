from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
from flask import *
import os
import getlog
import analyselog

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route("/")
def mainpage():
    return render_template("mainpage.html")

@app.route("/", methods=["POST"])
def submitreport():
    session["fightsdict"] = ""
    session["priests"] = ""
    session["fights"] = ""
    errors=""
    reportid = request.form["reportid"]
    session["reportid"] = reportid
    print (reportid)
    
    if not reportid:
        errors = "Please enter the report to analyse"
        return render_template("mainpage.html",errors=errors)
    else:
        try:
            session["priests"],session["fights"],session["fightsdict"] = getlog.getpeople(reportid)

        except Exception as e:
            errors=e
            return render_template("mainpage.html", errors=errors)

        return redirect(url_for("playerselect"))

@app.route('/playerselect/')
def playerselect():
    return render_template("selections.html",priests=[x for x in session["priests"]],fights=session["fights"])


@app.route("/playerselect/", methods=["POST"])
def submitplayer():
    player = session["priests"][request.form["PlayerSelect"]]
    fight = session["fightsdict"][request.form["FightSelect"]]
    print(player,fight)
    session["results"] = analyselog.getresults(session["reportid"],str(player),str(fight[0]),str(fight[1]))
    return redirect(url_for("results"))

@app.route('/results/')
def results():
    return render_template("Results.html",

                           cpm = session["results"][0],
                           lenience = session["results"][1],
                           bftd = session["results"][2],
                           cont = session["results"][3],
                           contpercent = session["results"][4],
                           xalans = session["results"][5],
                           xalpercent = session["results"][6],
                           prydaz = session["results"][7],
                           prydazpercent = session["results"][8],
                           skjoldr = session["results"][9],
                           skjoldrpercent = session["results"][10],
                           nero = session["results"][11],
                           neropercent = session["results"][12]


                           )

if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
