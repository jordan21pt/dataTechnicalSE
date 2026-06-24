from unittest.mock import MagicMock, patch

import pytest
import requests

from datatechnicalse.downloader import ESMADownloader, WebClient


def test_webclient_get_success() -> None:
    mock_response = MagicMock()
    mock_response.content = b"fake content"
    mock_response.status_code = 200

    with patch(
        "datatechnicalse.downloader.requests.get", return_value=mock_response
    ):
        client = WebClient()
        result = client.get("http://fake-url.com")
        assert result == b"fake content"


def test_webclient_get_failure() -> None:
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404")

    with patch(
        "datatechnicalse.downloader.requests.get", return_value=mock_response
    ):
        client = WebClient()
        with pytest.raises(requests.HTTPError):
            client.get("http://fake-url.com")


def test_esma_downloader_finds_second_link() -> None:
    mock_xml = b"""
    <response>
        <result numFound="2">
            <doc>
                <str name="file_type">DLTINS</str>
                <str name="download_link">http://fake-url.com/first.zip</str>
            </doc>
            <doc>
                <str name="file_type">DLTINS</str>
                <str name="download_link">http://fake-url.com/second.zip</str>
            </doc>
        </result>
    </response>
    """
    mock_client = MagicMock()
    mock_client.get.return_value = mock_xml

    downloader = ESMADownloader(mock_client, "http://fake-url.com")
    link = downloader._find_the_link(mock_xml, 1)
    assert link == "http://fake-url.com/second.zip"


def test_esma_downloader_raises_if_not_enough_docs() -> None:
    mock_xml = b"""
    <response>
        <result numFound="1">
            <doc>
                <str name="file_type">DLTINS</str>
                <str name="download_link">http://fake-url.com/first.zip</str>
            </doc>
        </result>
    </response>
    """
    mock_client = MagicMock()
    mock_client.get.return_value = mock_xml

    downloader = ESMADownloader(mock_client, "http://fake-url.com")
    with pytest.raises(ValueError):
        downloader._find_the_link(mock_xml, 1)
