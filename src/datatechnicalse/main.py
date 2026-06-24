import logging
import os

from datatechnicalse.downloader import ESMADownloader, WebClient
from datatechnicalse.parser import XMLParser
from datatechnicalse.storage import Storage
from datatechnicalse.transformer import DataTransformer

_DEFAULT_URL = (
    "https://registers.esma.europa.eu/solr/esma_registers_firds_files/"
    "select?q=*&fq=publication_date:%5B2021-01-17T00:00:00Z"
    "+TO+2021-01-19T23:59:59Z%5D&wt=xml&indent=true&start=0&rows=100"
)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting pipeline...")

    url = os.environ.get("ESMA_URL", _DEFAULT_URL)
    output_path = os.environ.get("OUTPUT_PATH", "/tmp/output.csv")

    client = WebClient()
    downloader = ESMADownloader(client, url)
    zip_bytes = downloader.download_and_parse_xml()
    logger.info("Downloaded and parsed XML data.")

    parser = XMLParser()
    df = parser.parse(zip_bytes)
    logger.info("Parsed XML data into DataFrame.")

    transformer = DataTransformer()
    df = transformer.transform(df)
    logger.info(
        "Transformed DataFrame. Sample rows:\n%s", df.head().to_string()
    )

    storage = Storage(output_path)
    storage.save(df)
    logger.info("Saved transformed data.")


if __name__ == "__main__":
    main()
