import requests

# getting the new content
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
    maxLength = max(maxLength, len(line) + 10)

lines.reverse()

# printing the top-most results
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

# adding to past results
for line in lines:
    if(not seenBefore(line)):
        addCurrent(line)
