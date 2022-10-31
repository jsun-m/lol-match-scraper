from spider import LeagueSpider

def crawl(username):
    lol_spider = LeagueSpider()
    lol_spider.start_crawl(username)

