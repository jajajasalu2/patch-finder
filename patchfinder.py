import argparse
from scrapy.crawler import CrawlerProcess
import patchfinder.spiders.default_spider as default_spider
import patchfinder.context as context
import patchfinder.settings as settings

def spawn_crawler(args):
    vuln = context.create_vuln(args.vuln_id)
    if not vuln: return False
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'ITEM_PIPELINES': {
            'patchfinder.spiders.pipelines.PatchPipeline': 300
        },
        'DEPTH_LIMIT': args.depth,
        'LOG_ENABLED': args.log
    })
    process.crawl(default_spider.DefaultSpider,
                  vuln=vuln,
                  patch_limit=args.patch_limit,
                  important_domains=args.imp_domains,
                  deny_domains=args.deny_domains)
    process.start()
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('vuln_id',
                        help='The vulnerability ID to find patches for')
    parser.add_argument('-d', '--depth', type=int,
                        default=settings.DEPTH_LIMIT,
                        help='The maximum depth the crawler should go to')
    parser.add_argument('-p', '--patch_limit', type=int,
                        default=settings.PATCH_LIMIT,
                        help='The maximum number of patches to be collected')
    parser.add_argument('-dd', '--deny_domains', nargs='+',
                        default=settings.DENY_DOMAINS,
                        help='Domains to avoid crawling')
    parser.add_argument('-id', '--imp_domains', nargs='+',
                        default=settings.IMPORTANT_DOMAINS,
                        help='Domains to prioritize crawling')
    parser.add_argument('-nl', '--no_log', dest='log', action='store_false',
                        help='Disable Scrapy logging')
    parser.set_defaults(log=True)
    args = parser.parse_args()
    spawn_return = spawn_crawler(args)
    if spawn_return:
        print('Crawling completed.')
    else:
        print('Can\'t recognize that vulnerability.')
