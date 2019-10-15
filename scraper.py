import requests
import datetime
from tinydb import TinyDB, Query

# getting the latest content
def getContent():
    content = requests.get("https://news.ycombinator.com/").text
    entries = content.split("\n")
    lines = []; maxLength = 0

    for entry in entries:
        if("<span class=\"rank\">" not in entry):
            continue

        rank = entry.split("class=\"rank\"")[1].split(">")[1].split(".")[0]
        link = entry.split("td class=\"title\"")[1].split(">")[1].split("<a href=\"")[1].split("\"")[0]
        title = entry.split("class=\"storylink\"")[1].split(">")[1].split("</a")[0]

        line = rank + title + link
        lines.insert(0, (rank, title, link))
        maxLength = max(maxLength, len(line))
    
    lines.reverse()
    return (lines, maxLength)

# printing the top-most results
def checkContent(lines, logFilePath):
    if(len(lines) != 30):
        f = open(logFilePath, "a")
        f.write(str(datetime.datetime.utcnow()) + " -- WARNING -- Less than 30 articles read! Only {} scraped.\n".format(len(lines)))
        f.close()
        
# printing the top-most results
def printContent(lines):
    class bcolors:
        pink = '\033[95m'
        blue = '\033[94m'
        green = '\033[92m'
        orange = '\033[93m'
        red = '\033[91m'
        unbold = '\033[0m'
        bold = '\033[1m'
        underline = '\033[4m'
    for line in lines:
        print(bcolors.bold + bcolors.red + line[0] + ". " + bcolors.orange + line[1] + ": " + bcolors.pink + line[2])

# checking no collisions
def seenBefore(line, db):
    return db.count((Query().title == line[1]) & (Query().link == line[2])) != 0

# adding to past results
def storeContent(lines, dbFilePath):
    db = TinyDB(dbFilePath)

    for line in lines:
        if(not seenBefore(line, db)):
            db.insert({'currentRank': int(line[0]), 'title': line[1], 'link': line[2]})

# put everything together
def main():
    logFilePath = "app.log"
    dbFilePath = "db.json"
    (lines, maxLength) = getContent()

    checkContent(lines, logFilePath)
    printContent(lines)

    storeContent(lines, dbFilePath)

if __name__ == "__main__":
    main()
