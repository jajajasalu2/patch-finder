from urllib.parse import urlparse
from scrapy.http import Request
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
import scrapy
from patchfinder.debian import DebianParser
import patchfinder.spiders.items as items
import patchfinder.entrypoint as entrypoint

class DefaultSpider(scrapy.Spider):
    """Scrapy Spider to extract patches

    Inherits from scrapy.Spider
    This spider would run by default

    Attributes:
        name: Name of the spider
        recursion_limit: The recursion depth the spider would go to
        patches: A list of patch links the spider has found
        deny_domains: A list of domains to deny crawling links of
        important_domains: A list of domains with higher crawling priority
        patch_limit: A threshold for the number of patches to collect
    """

    deny_domains = ['facebook.com', 'twitter.com']
    important_domains = []
    patch_limit = 100
    allowed_keys = {'deny_domains', 'important_domains', 'patch_limit'}

    def __init__(self, *args, **kwargs):
        self.name = 'default_spider'
        self.vuln_id = kwargs.get('vuln').vuln_id
        self.start_urls = kwargs.get('vuln').entrypoint_URLs
        self.patches = []
        self.__dict__.update((k, v) for k, v in kwargs.items() \
                             if k in self.allowed_keys)
        super(DefaultSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        for url in self.start_urls:
            if url.startswith('https://security-tracker.debian.org'):
                yield Request(url, callback=self.parse_debian)
            else:
                yield Request(url, callback=self.parse)

    def parse_debian(self, response):
        debian_parser = DebianParser()
        patches = debian_parser.parse(self.vuln_id)
        for patch in patches:
            if len(self.patches) < self.patch_limit:
                self.add_patch(patch['patch_link'])
                yield patch

    def parse(self, response):
        xpaths = entrypoint.get_xpath(response.url)
        links = LxmlLinkExtractor(deny_domains=self.deny_domains,
                                  restrict_xpaths=xpaths) \
                                          .extract_links(response)
        for link in links:
            link = response.urljoin(link.url[0:])
            patch_link = entrypoint.is_patch(link)
            if patch_link and len(self.patches) < self.patch_limit:
                if patch_link not in self.patches:
                    patch = items.Patch()
                    patch['patch_link'] = patch_link
                    patch['reaching_path'] = response.url
                    self.add_patch(patch_link)
                    yield patch
            elif len(self.patches) < self.patch_limit:
                priority = self.domain_priority(link)
                yield Request(link, callback=self.parse, priority=priority)

    def domain_priority(self, url):
        domain = urlparse(url).hostname
        if domain in self.important_domains:
            return 1
        return 0

    def add_patch(self, patch_link):
        self.patches.append(patch_link)
