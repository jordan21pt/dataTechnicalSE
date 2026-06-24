import io
import zipfile

import pytest

from datatechnicalse.parser import XMLParser

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


def create_fake_zip(xml_content: str) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("test.xml", xml_content)
    return buffer.getvalue()


def test_parser_extracts_correct_columns() -> None:
    parser = XMLParser()
    zip_bytes = create_fake_zip(_SAMPLE_XML)
    df = parser.parse(zip_bytes)
    assert list(df.columns) == [
        "FinInstrmGnlAttrbts.Id",
        "FinInstrmGnlAttrbts.FullNm",
        "FinInstrmGnlAttrbts.ClssfctnTp",
        "FinInstrmGnlAttrbts.CmmdtyDerivInd",
        "FinInstrmGnlAttrbts.NtnlCcy",
        "Issr",
    ]


def test_parser_extracts_correct_values() -> None:
    parser = XMLParser()
    zip_bytes = create_fake_zip(_SAMPLE_XML)
    df = parser.parse(zip_bytes)
    assert df.iloc[0]["FinInstrmGnlAttrbts.Id"] == "TEST123"
    assert df.iloc[0]["FinInstrmGnlAttrbts.FullNm"] == "Test banana"
    assert df.iloc[0]["FinInstrmGnlAttrbts.ClssfctnTp"] == "RWSNCA"
    assert df.iloc[0]["FinInstrmGnlAttrbts.CmmdtyDerivInd"] == "false"
    assert df.iloc[0]["FinInstrmGnlAttrbts.NtnlCcy"] == "EUR"
    assert df.iloc[0]["Issr"] == "TEST_ISSR"


def test_parser_no_xml_in_zip() -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("test.txt", "not xml")
    parser = XMLParser()
    with pytest.raises(ValueError):
        parser.parse(buffer.getvalue())
