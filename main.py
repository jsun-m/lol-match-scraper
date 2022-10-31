import sys
from spider import LeagueSpider

def crawl(username):
    lol_spider = LeagueSpider()
    lol_spider.start_crawl(username)


if __name__ == "__main__":
    username = sys.args[1]
    crawl(username)
