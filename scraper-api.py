import os
import sys
import json
import requests
from tinydb import TinyDB, Query

# getting the latest content
def getContent():
    ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty").json()
    return ids[:30]

# printing the top-most results
def printContent(source):
    class bcolors:
        pink = '\033[95m'
        blue = '\033[94m'
        green = '\033[92m'
        orange = '\033[93m'
        red = '\033[91m'
        unbold = '\033[0m'
        bold = '\033[1m'
        underline = '\033[4m'

    for story in source:
        newlineRequired = False
        try:
            print(bcolors.bold + bcolors.blue + 'id:' + story['id'] + " ", end = "")
            newlineRequired = True
        except:
            pass
        try:
            print(bcolors.bold + bcolors.red + 'time:' + story['timestamp'] + " ", end = "")
            newlineRequired = True
        except:
            pass
        try:
            print(bcolors.bold + bcolors.orange + story['title'] + ": ", end="")
            newlineRequired = True
        except:
            pass
        try:
            print(bcolors.bold + bcolors.pink + story['link'], end="")
            newlineRequired = True
        except:
            pass
        if(newlineRequired):
            print()

# checking no collisions
def seenBefore(story, db):
    return db.count((Query().title == story['title']) & (Query().link == story['link'])) != 0

# adding to past results
def storeContent(ids, db, printing = False):
    # use for printing later
    top = []

    for id in ids:
        story = requests.get("https://hacker-news.firebaseio.com/v0/item/" + str(id) + ".json?print=pretty").json()
        reducedStory = {'id': str(story['id']), 'timestamp': str(story['time']), 'title': story['title'], 'link': story['url']}
        if(printing):
            printContent([reducedStory])

        # this is not really relevant as articles do not
        # tend to come up again unless really relevant
        # however it does protect against articles staying
        # in the top for longer than 4 hours
        # print(db.count((Query().title != story['title']) & (Query().link != story['url'])))
        if(not seenBefore(reducedStory, db)):
            db.insert(reducedStory)

        # print for top results whether it appeared or not
        top.append(reducedStory)

    return top

# put everything together
def main(whatToShow = 0, logFilePath = os.path.dirname(os.path.realpath(__file__)) + "/app.log", dbFilePath = os.path.dirname(os.path.realpath(__file__)) + "/db.json"):
    db = TinyDB(dbFilePath)

    if(whatToShow == 0):
        ids = getContent()
        top = storeContent(ids, db, printing = True)
        # printContent(top)

    elif(whatToShow == 1):
        printContent(db.all())

    elif(whatToShow == 2):
        ids = getContent()
        top = storeContent(ids, db)

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
