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
def printContent(source, traits):
    for story in source:
        # if story has any field at all
        newlineRequired = False

        # print the specific field of the story
        # with all the fields on the same line
        # some stories may not have some fields
        for (colour, name, field) in traits:
            try:
                print(colour + name + ': ' + story[field] + ' ', end='')
                newlineRequired = True
            except:
                pass

        if(newlineRequired):
            print()

# checking no collisions
def seenBefore(story, db):
    return db.count((Query().title == story['title']) & (Query().link == story['link'])) != 0

# adding to past results
def storeContent(ids, db, traits):
    # use for printing later
    top = []

    for id in ids:
        story = requests.get("https://hacker-news.firebaseio.com/v0/item/" + str(id) + ".json?print=pretty").json()
        
        # some stories do not have urls
        reducedStory = {}
        for (colour, field, myField) in traits:
            try:
                reducedStory[myField] = str(story[field])
            except:
                reducedStory[myField] = "not existent"

        # this is not really relevant as articles do not
        # tend to come up again unless really relevant
        # however it does protect against articles staying
        # in the top for longer than 4 hours
        if(not seenBefore(reducedStory, db)):
            db.insert(reducedStory)

        # print for top results whether it appeared or not
        top.append(reducedStory)

    return top

# put everything together
def main(whatToShow = 0, logFilePath = os.path.dirname(os.path.realpath(__file__)) + "/app.log", dbFilePath = os.path.dirname(os.path.realpath(__file__)) + "/db.json"):
    db = TinyDB(dbFilePath)
    class bcolors:
        pink = '\033[95m'
        blue = '\033[94m'
        green = '\033[92m'
        orange = '\033[93m'
        red = '\033[91m'
        unbold = '\033[0m'
        bold = '\033[1m'
        underline = '\033[4m'

    traits = []
    traits.append((bcolors.bold + bcolors.blue, 'id', 'id'))
    traits.append((bcolors.bold + bcolors.red, 'time', 'timestamp'))
    traits.append((bcolors.bold + bcolors.orange, 'title', 'title'))
    traits.append((bcolors.bold + bcolors.pink, 'url', 'link'))

    if(whatToShow == 0):
        ids = getContent()
        top = storeContent(ids, db, traits)
        printContent(top, traits)

    elif(whatToShow == 1):
        printContent(db.all(), traits)

    elif(whatToShow == 2):
        ids = getContent()
        storeContent(ids, db, traits)

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
