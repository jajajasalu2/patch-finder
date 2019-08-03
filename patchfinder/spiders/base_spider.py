"""Provides Base Scrapy spider.

Attributes:
    logger: Module level logger.
"""
import logging
import json
import scrapy
import patchfinder.context as context
import patchfinder.settings as settings
from patchfinder.entrypoint import Resource
import dicttoxml

logger = logging.getLogger(__name__)


class BaseSpider(scrapy.Spider):
    """Base Scrapy Spider.

    This spider has functionalities that can be used by successive spiders.

    Attributes:
        name (str): Name of the spider.
    """

    def __init__(self, name):
        self.name = name

    def parse(self, response):
        """Parse the given response.

        The relevant parse callable for the response is determined and items are
        generated from it.

        Args:
            response (scrapy.Response): A response object.

        Yields:
            (str or scrapy.Item or scrapy.http.Request):
                Items/Requests generated from the parse callable.
        """
        parse_callable = self._callback(response)
        if parse_callable:
            yield from parse_callable(response)

    def parse_default(self, response):
        """Default parse method.

        The response is parsed as per the necessary xpath(s).

        Args:
            response (scrapy.http.Response): A response object

        Yields:
            (str or scrapy.Item or scrapy.http.Response):
                Items/Requests generated from the response.
        """
        yield from self._generate_items_and_requests(response)

    def parse_json(self, response):
        """Parse a JSON response.

        The response is converted to XML and then parsed as per the necessary
        xpath(s).

        Args:
            response (scrapy.http.Response): The Response object.

        Yields:
            (str or scrapy.Item or scrapy.http.Request):
                Items/Requests generated from the response.
        """
        response = self._json_response_to_xml(response)
        yield from self._generate_items_and_requests(response)

    @staticmethod
    def _json_response_to_xml(response):
        """Convert a JSON response to XML.

        This enables parsing the JSON with Xpaths.

        Args:
            response (scrapy.http.Response): A response object.

        Yields:
            scrapy.http.Response: The same response with an XML body.
        """
        dictionary = json.loads(response.body.decode())
        xml = dicttoxml.dicttoxml(dictionary)
        return response.replace(body=xml)

    def _generate_items_and_requests(self, response):
        """str: Yields scraped items."""
        yield from self._scrape(response)

    #TODO: Should yield Item objects rather than strings.
    def _scrape(self, response):
        """Scrape a given response.

        Items are scraped from the response w/r/t the response's normal xpaths.
        These items are then yielded.

        Args:
            response (scrapy.http.Response): A Response object.

        Yields:
            str: Items scraped from the response.
        """
        xpaths = Resource.get_resource(response.url).normal_xpaths
        for xpath in xpaths:
            scraped_items = response.xpath(xpath).extract()
            for item in scraped_items:
                yield item

    def _callback(self, response):
        """Returns the callback method for a response.

        The callback method is used to parse the response. It can be based on
        the content-type of the response or on the response URL itself, since
        certain URLs can warrant using a different parse method altogether.

        Args:
            response (scrapy.http.Response):
                The response for which the callable is to be determined.

        Returns:
            callable: A parse callable.
        """
        callback = self._callback_by_url(response)
        if not callback:
            callback = self._callback_by_content(response)
        return callback

    def _callback_by_url(self, response):
        """Returns the parse callable based on the response URL.

        Args:
            response (scrapy.http.Response):
                The response for which the callable is to be determined.

        Returns:
            callable: A parse callable.
        """
        return None

    def _callback_by_content(self, response):
        """Returns the parse callable based on the response's content-type.

        Args:
            response (scrapy.http.Response): A Response object.

        Returns:
            callable: A parse callable.
        """
        callback = None
        if "Content-Type" not in response.headers:
            return callback
        content_type = response.headers["Content-Type"].decode()
        if content_type.startswith("application/json"):
            callback = self.parse_json
        else:
            callback = self.parse_default
        return callback
