import logging
import xml.etree.ElementTree as ET

import requests

logger = logging.getLogger(__name__)


class WebClient:
    """Generic HTTP client for GET requests."""

    def __init__(self, timeout: int = 30) -> None:
        """Initialize the WebClient.

        Args:
            timeout: Max waiting time in seconds
        """
        self.timeout = timeout

    def get(self, url: str) -> bytes:
        """Makes a GET request to the given URL.

        Args:
            url: URL to make the request

        Returns:
            Answer will be returned in bytes, because we
            need to get a zip file.

        Raises:
            requests.HTTPError: If the request fails.
        """
        logger.info("Fetching URL: %s", url)
        try:
            res = requests.get(url, timeout=self.timeout)
            res.raise_for_status()
            logger.info(
                "Request successfull with status code: %d", res.status_code
            )
            return res.content
        except requests.HTTPError as e:
            logger.error("Was not possible to make the request: %s", e)
            raise


class ESMADownloader:
    """Generic class to download XMLs from ESMA"""

    def __init__(self, web_client: WebClient, url: str) -> None:
        """Initialize the ESMADownloader.

        Args:
            web_client: An instance of WebClient
            url: The URL to download XML from
        """
        self._web_client = web_client
        self._url = url

    def download_and_parse_xml(self) -> bytes:
        """Function that orchestrates the logic of downloading the
        XML and parse it to find the final link to download the ZIP.

        Returns:
            Answer will be returned in bytes, because we
            need to get a zip file.
        """
        xml_bytes = self._web_client.get(self._url)
        link = self._find_the_link(xml_bytes, 1)
        logger.info(" the final link: %s", link)
        return self._web_client.get(link)

    def _find_the_link(self, xml_bytes: bytes, link_pos: int) -> str:
        """Private function with the logic to find the right link.
        It also makes sure there are at list link_pos+1 elements,
        or else it raises an Error.
        Also makes sure we filter the file_type as "DLTINS".

        Args:
            xml_bytes: The response from the request made
            link_pos: The position of the link that we want
            to download the zip from

        Returns:
            The download link URL as a string.

        Raises:
            ValueError: If there are less then link_pos+1 links.
        """
        root = ET.fromstring(xml_bytes)
        number_docs = int(root.find(".//result").attrib["numFound"])
        if number_docs < (link_pos + 1):
            logger.error("Expected at least 2 docs, found %d", number_docs)
            raise ValueError("Not enough docs found")

        docs = root.findall(".//doc")
        dltins = [
            d
            for d in docs
            if d.find('.//str[@name="file_type"]').text == "DLTINS"
        ]
        return dltins[link_pos].find('.//str[@name="download_link"]').text
