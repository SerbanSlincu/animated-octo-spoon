import os
import sys
import json
import requests
import datetime
from tinydb import TinyDB, Query

# getting the latest content
def getContent(traits):
    content = requests.get("https://news.ycombinator.com/").text
    entries = content.split("\n")

    stories = []

    for entry in entries:
        if("<span class=\"rank\">" not in entry):
            continue

        rank = entry.split("class=\"rank\"")[1].split(">")[1].split(".")[0]
        link = entry.split("td class=\"title\"")[1].split(">")[1].split("<a href=\"")[1].split("\"")[0]
        title = entry.split("class=\"storylink\"")[1].split(">")[1].split("</a")[0]
        story = {'timestamp': str(datetime.datetime.utcnow()), 'currentRank': rank, 'title': title, 'link': link}

        # some stories may not have some properties defined in traits
        reducedStory = {}
        for (colour, field, myField) in traits:
            try:
                reducedStory[myField] = str(story[myField])
            except:
                reducedStory[myField] = "not existent"

        stories.append(reducedStory)
    
    return stories

# checking the top-most results and the HTML content has not changed
def checkContent(stories, logFilePath):
    if(len(stories) != 30):
        f = open(logFilePath, "a")
        f.write(str(datetime.datetime.utcnow()) + " -- WARNING -- Less than 30 articles read! Only {} scraped.\n".format(len(stories)))
        f.close()
        
# printing the top-most results
def printContent(stories, traits):
    for story in stories:
        # story may not have any fields
        # so no point in printing new line
        newlineRequired = False

        # print the specific field of the story
        # with all the fields on the same line
        # some stories may not have some fields
        for (colour, name, field) in traits:
            try:
                print(colour + name + story[field] + ' ', end='')
                newlineRequired = True
            except:
                pass
        if(newlineRequired):
            print()

# checking no collisions
def seenBefore(story, db):
    return db.count((Query().title == story['title']) & (Query().link == story['link'])) != 0

# adding to past results
def storeContent(stories, db):
    for story in stories:
        # this is not relevant as articles do not
        # tend to come up again unless really relevant
        # however it does protect against articles staying
        # in the top for longer than 4 hours
        if(not seenBefore(story, db)):
            db.insert(story)

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
    traits.append((bcolors.bold + bcolors.blue, '', 'currentRank'))
    traits.append((bcolors.bold + bcolors.red, '', 'timestamp'))
    traits.append((bcolors.bold + bcolors.orange, 'title: ', 'title'))
    traits.append((bcolors.bold + bcolors.pink, 'url: ', 'link'))

    if(whatToShow == 1):
        printContent(db.all(), traits)
    else:
        stories = getContent(traits)
        checkContent(stories, logFilePath)
        storeContent(stories, db)

        if(whatToShow == 0):
            printContent(stories, traits)
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
