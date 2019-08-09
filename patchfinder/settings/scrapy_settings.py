"""Scrapy Core settings.

These settings will be passed into the CrawlerProcess which will initiate the
crawling process.
"""

USER_AGENT = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)"
DEPTH_LIMIT = 1
EXTENSIONS = {
    "scrapy.extensions.telnet.TelnetConsole": None,
    "scrapy.extensions.corestats.CoreStats": None,
    "scrapy.extensions.memusage.MemoryUsage": None,
    "scrapy.extensions.logstats.LogStats": None,
}
SPIDER_MIDDLEWARES = {
    "patchfinder.spiders.middlewares.DepthResetMiddleware": 850
}
DOWNLOADER_MIDDLEWARES = {
    "patchfinder.spiders.middlewares.ContentTypeFilterDownloaderMiddleware": 1000
}
