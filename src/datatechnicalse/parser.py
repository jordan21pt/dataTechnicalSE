import io
import logging
import xml.etree.ElementTree as ET
import zipfile

import pandas as pd

logger = logging.getLogger(__name__)


class XMLParser:
    """Generic class for parsing a XML file"""

    def parse(self, zip_bytes: bytes) -> pd.DataFrame:
        """Extract XML file from zip if found. Creates a pandas DataFrame
        with given columns.

        Args:
            zip_bytes: The ZIP in bytes.

        Returns:
            A pandas DataFrame with the parsed records.

        Raises:
            ValueError: If a XML file is not found.
        """
        xml_bytes = self._extract_xml(zip_bytes)
        root = ET.fromstring(xml_bytes)
        ns = {"ns": "urn:iso:std:iso:20022:tech:xsd:auth.036.001.02"}

        records = root.findall(".//ns:ModfdRcrd", ns)
        logger.info("Found %d records", len(records))

        rows = []
        for rec in records:
            row = {
                "FinInstrmGnlAttrbts.Id": self._get_text(
                    rec, "ns:FinInstrmGnlAttrbts/ns:Id", ns
                ),
                "FinInstrmGnlAttrbts.FullNm": self._get_text(
                    rec, "ns:FinInstrmGnlAttrbts/ns:FullNm", ns
                ),
                "FinInstrmGnlAttrbts.ClssfctnTp": self._get_text(
                    rec, "ns:FinInstrmGnlAttrbts/ns:ClssfctnTp", ns
                ),
                "FinInstrmGnlAttrbts.CmmdtyDerivInd": self._get_text(
                    rec, "ns:FinInstrmGnlAttrbts/ns:CmmdtyDerivInd", ns
                ),
                "FinInstrmGnlAttrbts.NtnlCcy": self._get_text(
                    rec, "ns:FinInstrmGnlAttrbts/ns:NtnlCcy", ns
                ),
                "Issr": self._get_text(rec, "ns:Issr", ns),
            }
            rows.append(row)
        return pd.DataFrame(rows)

    def _extract_xml(self, zip_bytes: bytes) -> bytes:
        """Extracts XML file from the ZIP file.

        Args:
            zip_bytes: The ZIP in bytes.

        Returns:
            The XML in bytes.

        Raises:
            ValueError: If a XML file is not found.
        """
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            for name in zf.namelist():
                if name.endswith(".xml"):
                    with zf.open(name) as xml_file:
                        return xml_file.read()
            raise ValueError("Didn't find a XML file in the zip")

    def _get_text(
        self, element: ET.Element, path: str, ns: dict[str, str]
    ) -> str | None:
        """Get text from an XML element safely.

        Args:
            element: The XML element to search in.
            path: The path to the element.
            ns: The namespace dictionary.

        Returns:
            The text of the element or None if not found.
        """
        found = element.find(path, ns)
        return found.text if found is not None else None
