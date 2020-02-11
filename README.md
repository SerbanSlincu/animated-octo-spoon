# YCombinator Hackers News Scraper 
The purpose of this tool is to scrape news.ycombinator.com/ and constantly store the top 30 results. 
There are two implementations available, one of them is based on the YC-API (https://github.com/HackerNews/API), while the other one is based on a personal scraper based on HTML classes.

### Comparison
- The API version is much slower, because it needs to do 30 pages more than the personal version.
- However, the API version may be more usable than the other one, because it relies on the official API.

### Use case
- Pass 0 or leave empty for **most recent results** (print and scrape)
- Pass 1 for **all scraped results**
- Pass 2 to **scrape most recent results** (just scrape, useful for doing in the background)

Also pass the **log** and the **database** file paths.

###### Example
e.g. **$ python3 scraper.py 1 app.log db.json**
for printing all results stored in the database

