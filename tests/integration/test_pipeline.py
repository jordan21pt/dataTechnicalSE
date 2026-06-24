import io
import zipfile
from unittest.mock import MagicMock

import pandas as pd

from datatechnicalse.downloader import ESMADownloader
from datatechnicalse.parser import XMLParser
from datatechnicalse.storage import Storage
from datatechnicalse.transformer import DataTransformer

_SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<BizData xmlns="urn:iso:std:iso:20022:tech:xsd:head.003.001.01">
    <Pyld>
        <Document xmlns="urn:iso:std:iso:20022:tech:xsd:auth.036.001.02">
            <FinInstrmRptgRefDataDltaRpt>
                <FinInstrm>
                    <ModfdRcrd>
                        <FinInstrmGnlAttrbts>
                            <Id>TEST123</Id>
                            <FullNm>Test banana</FullNm>
                            <ClssfctnTp>RWSNCA</ClssfctnTp>
                            <CmmdtyDerivInd>false</CmmdtyDerivInd>
                            <NtnlCcy>EUR</NtnlCcy>
                        </FinInstrmGnlAttrbts>
                        <Issr>TEST_ISSR</Issr>
                    </ModfdRcrd>
                </FinInstrm>
            </FinInstrmRptgRefDataDltaRpt>
        </Document>
    </Pyld>
</BizData>"""


mock_esma_xml = b"""
<response>
    <result numFound="2">
        <doc>
            <str name="file_type">DLTINS</str>
            <str name="download_link">http://fake.com/first.zip</str>
        </doc>
        <doc>
            <str name="file_type">DLTINS</str>
            <str name="download_link">http://fake.com/second.zip</str>
        </doc>
    </result>
</response>
"""


def create_fake_zip(xml_content: str) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("test.xml", xml_content)
    return buffer.getvalue()


fake_zip = create_fake_zip(_SAMPLE_XML)


def test_pipeline_integration() -> None:
    # Mock the WebClient to return the mock ESMA XML and fake ZIP
    mock_client = MagicMock()
    mock_client.get.side_effect = [mock_esma_xml, fake_zip]

    # Initialize the downloader with the mocked client
    downloader = ESMADownloader(mock_client, "http://fake-url.com")
    zip_bytes = downloader.download_and_parse_xml()

    # Parse the XML from the ZIP
    parser = XMLParser()
    df = parser.parse(zip_bytes)

    # Transform the DataFrame
    transformer = DataTransformer()
    transformed_df = transformer.transform(df)

    # Save the transformed DataFrame to a temporary path
    output_path = "/tmp/test_output.csv"
    storage = Storage(output_path)
    storage.save(transformed_df)

    # Read back the saved CSV and verify its contents
    saved_df = pd.read_csv(output_path)
    assert not saved_df.empty
    assert "FinInstrmGnlAttrbts.Id" in saved_df.columns
