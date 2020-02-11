import os
import sys
import json
import requests
import datetime
from tinydb import TinyDB, Query

# getting the latest content
def getContent():
    content = requests.get("https://news.ycombinator.com/").text
    entries = content.split("\n")

    lines = []
    maxLength = 0

    for entry in entries:
        if("<span class=\"rank\">" not in entry):
            continue

        rank = entry.split("class=\"rank\"")[1].split(">")[1].split(".")[0]
        link = entry.split("td class=\"title\"")[1].split(">")[1].split("<a href=\"")[1].split("\"")[0]
        title = entry.split("class=\"storylink\"")[1].split(">")[1].split("</a")[0]

        line = rank + title + link
        lines.append(json.dumps({'timestamp': str(datetime.datetime.utcnow()), 'currentRank': rank, 'title': title, 'link': link}))
        maxLength = max(maxLength, len(line))
    
    return (lines, maxLength)

# printing the top-most results
def checkContent(lines, logFilePath):
    if(len(lines) != 30):
        f = open(logFilePath, "a")
        f.write(str(datetime.datetime.utcnow()) + " -- WARNING -- Less than 30 articles read! Only {} scraped.\n".format(len(lines)))
        f.close()
        
# printing the top-most results
def printContent(lines, load = False):
    class bcolors:
        pink = '\033[95m'
        blue = '\033[94m'
        green = '\033[92m'
        orange = '\033[93m'
        red = '\033[91m'
        unbold = '\033[0m'
        bold = '\033[1m'
        underline = '\033[4m'

    if(load):
        for line in lines:
            newlineRequired = False
            line = json.loads(line)
            try:
                print(bcolors.bold + bcolors.red + line['currentRank'] + ". ", end="")
                newlineRequired = True
            except:
                pass
            try:
                print(bcolors.bold + bcolors.orange + line['title'] + ": ", end="")
                newlineRequired = True
            except:
                pass
            try:
                print(bcolors.bold + bcolors.pink + line['link'], end="")
                newlineRequired = True
            except:
                pass
            if(newlineRequired):
                print()
    else:
        for line in lines:
            newlineRequired = False
            try:
                print(bcolors.bold + bcolors.red + line['timestamp'] + " ", end = "")
                newlineRequired = True
            except:
                pass
            try:
                print(bcolors.bold + bcolors.orange + line['title'] + ": ", end = "")
                newlineRequired = True
            except:
                pass
            try:
                print(bcolors.bold + bcolors.pink + line['link'], end = "")
                newlineRequired = True
            except:
                pass
            if(newlineRequired):
                print()
            

# checking no collisions
def seenBefore(line, db):
    return db.count((Query().title == line['title']) & (Query().link == line['link'])) != 0

# adding to past results
def storeContent(lines, db):
    for line in lines:
        line = json.loads(line)

        # this is not relevant as articles do not
        # tend to come up again unless really relevant
        # print(db.count((Query().title != line['title']) & (Query().link != line['link'])))
        # if(not seenBefore(line, db)):
        db.insert({'timestamp': str(datetime.datetime.utcnow()), 'currentRank': int(line['currentRank']), 'title': line['title'], 'link': line['link']})

# put everything together
def main(whatToShow = 0, logFilePath = os.path.dirname(os.path.realpath(__file__)) + "/app.log", dbFilePath = os.path.dirname(os.path.realpath(__file__)) + "/db.json"):
    db = TinyDB(dbFilePath)
    (lines, maxLength) = getContent()

    checkContent(lines, logFilePath)
    storeContent(lines, db)

    if(whatToShow == 0):
        printContent(lines, True)
    elif(whatToShow == 1):
        printContent(db.all())
    elif(whatToShow == 2):
        pass

if __name__ == "__main__":
    if(len(sys.argv) > 1):
        main(int(sys.argv[1]), sys.argv[2], sys.argv[3])
    else:
        main()
        print()
        print("+------------------------------------------------+")
        print("| Pass 0 or leave empty for most recent results. |")
        print("| Pass 1 for all scraped results.                |")
        print("| Pass 2 to scrape new results.                  |")
        print("| Also pass the log and the db files.            |")
        print("| e.g. $ python3 scraper.py 1 app.log db.json    |")
        print("+------------------------------------------------+")
