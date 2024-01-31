import unittest
import xml.etree.ElementTree as ET
from app.symbolic.split_part_to_systems import split_part_to_systems


class SplitSystemsTest(unittest.TestCase):
    def assert_xml_equals(self, expected: str, given: ET.Element):
        e = ET.canonicalize(
            expected,
            strip_text=True
        )
        g = ET.canonicalize(
            ET.tostring(given),
            strip_text=True
        )
        self.assertEqual(e, g)

    def test_it_does_not_split_single_system(self):
        part = ET.fromstring("""
        <part>
            <measure number="1">
                <note>A</note>
            </measure>
            <measure number="2">
                <note>B</note>
            </measure>
        </part>
        """)

        pages = split_part_to_systems(part)

        assert len(pages) == 1
        
        page = pages[0]
        assert len(page.systems) == 1
        self.assert_xml_equals("""
        <part>
            <measure number="1">
                <note>A</note>
            </measure>
            <measure number="2">
                <note>B</note>
            </measure>
        </part>
        """, page.systems[0].part)

    def test_it_splits_systems_to_pages(self):
        part = ET.fromstring("""
        <part>
            <measure number="1">
                <note>A</note>
            </measure>
            <measure number="2">
                <note>B</note>
            </measure>

            <measure number="3">
                <print new-system="yes"></print>
                <note>C</note>
            </measure>
            <measure number="4">
                <note>D</note>
            </measure>

            <measure number="5">
                <print new-page="yes"></print>
                <note>E</note>
            </measure>
            <measure number="6">
                <note>F</note>
            </measure>
        </part>
        """)

        pages = split_part_to_systems(part)

        assert len(pages) == 2
        
        page = pages[0]
        assert len(page.systems) == 2
        self.assert_xml_equals("""
        <part>
            <measure number="1">
                <note>A</note>
            </measure>
            <measure number="2">
                <note>B</note>
            </measure>
        </part>
        """, page.systems[0].part)
        self.assert_xml_equals("""
        <part>
            <measure number="3">
                <print new-system="yes"></print>
                <note>C</note>
            </measure>
            <measure number="4">
                <note>D</note>
            </measure>
        </part>
        """, page.systems[1].part)

        page = pages[1]
        assert len(page.systems) == 1
        self.assert_xml_equals("""
        <part>
            <measure number="5">
                <print new-page="yes"></print>
                <note>E</note>
            </measure>
            <measure number="6">
                <note>F</note>
            </measure>
        </part>
        """, page.systems[0].part)

    def test_it_emits_explicit_header(self):
        part = ET.fromstring("""
        <part>
            <measure number="1">
                <attributes>
                    <divisions>6</divisions>
                    <key><fifths>0</fifths></key>
                    <time><beats>3</beats><beat-type>4</beat-type></time>
                    <staves>2</staves>
                    <clef number="1"><sign>G</sign><line>2</line></clef>
                    <clef number="2"><sign>F</sign><line>4</line></clef>
                </attributes>
                <note>A</note>
            </measure>
            <measure number="2">
                <note>B</note>
            </measure>

            <measure number="3">
                <print new-system="yes"></print>
                <note>C</note>
            </measure>
            <measure number="4">
                <note>D</note>
            </measure>
        </part>
        """)

        pages = split_part_to_systems(part)

        assert len(pages) == 1
        page = pages[0]
        assert len(page.systems) == 2
        self.assert_xml_equals("""
        <part>
            <measure number="1">
                <attributes>
                    <divisions>6</divisions>
                    <key><fifths>0</fifths></key>
                    <time><beats>3</beats><beat-type>4</beat-type></time>
                    <staves>2</staves>
                    <clef number="1"><sign>G</sign><line>2</line></clef>
                    <clef number="2"><sign>F</sign><line>4</line></clef>
                </attributes>
                <note>A</note>
            </measure>
            <measure number="2">
                <note>B</note>
            </measure>
        </part>
        """, page.systems[0].part)
        self.assert_xml_equals("""
        <part>
            <measure number="3">
                <print new-system="yes"></print>
                <attributes>
                    <key><fifths>0</fifths></key>
                    <clef number="1"><sign>G</sign><line>2</line></clef>
                    <clef number="2"><sign>F</sign><line>4</line></clef>
                </attributes>
                <note>C</note>
            </measure>
            <measure number="4">
                <note>D</note>
            </measure>
        </part>
        """, page.systems[1].part)
    
    def test_it_emits_explicit_header_in_existing_attributes(self):
        part = ET.fromstring("""
        <part>
            <measure number="1">
                <attributes>
                    <divisions>6</divisions>
                    <key><fifths>0</fifths></key>
                    <time><beats>3</beats><beat-type>4</beat-type></time>
                    <staves>2</staves>
                    <clef number="1"><sign>G</sign><line>2</line></clef>
                    <clef number="2"><sign>F</sign><line>4</line></clef>
                </attributes>
                <note>A</note>
            </measure>
            <measure number="2">
                <note>B</note>
            </measure>

            <measure number="3">
                <print new-system="yes"></print>
                <attributes>
                    <clef number="2"><sign>G</sign><line>2</line></clef>
                </attributes>
                <note>C</note>
            </measure>
            <measure number="4">
                <note>D</note>
            </measure>
        </part>
        """)

        pages = split_part_to_systems(part)

        assert len(pages) == 1
        page = pages[0]
        assert len(page.systems) == 2
        self.assert_xml_equals("""
        <part>
            <measure number="1">
                <attributes>
                    <divisions>6</divisions>
                    <key><fifths>0</fifths></key>
                    <time><beats>3</beats><beat-type>4</beat-type></time>
                    <staves>2</staves>
                    <clef number="1"><sign>G</sign><line>2</line></clef>
                    <clef number="2"><sign>F</sign><line>4</line></clef>
                </attributes>
                <note>A</note>
            </measure>
            <measure number="2">
                <note>B</note>
            </measure>
        </part>
        """, page.systems[0].part)
        self.assert_xml_equals("""
        <part>
            <measure number="3">
                <print new-system="yes"></print>
                <attributes>
                    <key><fifths>0</fifths></key>
                    <clef number="1"><sign>G</sign><line>2</line></clef>
                    <clef number="2"><sign>G</sign><line>2</line></clef>
                </attributes>
                <note>C</note>
            </measure>
            <measure number="4">
                <note>D</note>
            </measure>
        </part>
        """, page.systems[1].part)
    
    def test_it_emits_explicit_header_correctly_after_mid_measure_change(self):
        part = ET.fromstring("""
        <part>
            <measure number="1">
                <attributes>
                    <divisions>6</divisions>
                    <key><fifths>0</fifths></key>
                    <time><beats>3</beats><beat-type>4</beat-type></time>
                    <staves>2</staves>
                    <clef number="1"><sign>G</sign><line>2</line></clef>
                    <clef number="2"><sign>F</sign><line>4</line></clef>
                </attributes>
                <note>A</note>
            </measure>
            <measure number="2">
                <attributes>
                    <key><fifths>-2</fifths></key>
                    <clef number="2"><sign>G</sign><line>2</line></clef>
                </attributes>
                <note>B</note>
            </measure>

            <measure number="3">
                <print new-system="yes"></print>
                <note>C</note>
            </measure>
            <measure number="4">
                <note>D</note>
            </measure>
        </part>
        """)

        pages = split_part_to_systems(part)

        assert len(pages) == 1
        page = pages[0]
        assert len(page.systems) == 2
        self.assert_xml_equals("""
        <part>
            <measure number="1">
                <attributes>
                    <divisions>6</divisions>
                    <key><fifths>0</fifths></key>
                    <time><beats>3</beats><beat-type>4</beat-type></time>
                    <staves>2</staves>
                    <clef number="1"><sign>G</sign><line>2</line></clef>
                    <clef number="2"><sign>F</sign><line>4</line></clef>
                </attributes>
                <note>A</note>
            </measure>
            <measure number="2">
                <attributes>
                    <key><fifths>-2</fifths></key>
                    <clef number="2"><sign>G</sign><line>2</line></clef>
                </attributes>
                <note>B</note>
            </measure>
        </part>
        """, page.systems[0].part)
        self.assert_xml_equals("""
        <part>
            <measure number="3">
                <print new-system="yes"></print>
                <attributes>
                    <key><fifths>-2</fifths></key>
                    <clef number="1"><sign>G</sign><line>2</line></clef>
                    <clef number="2"><sign>G</sign><line>2</line></clef>
                </attributes>
                <note>C</note>
            </measure>
            <measure number="4">
                <note>D</note>
            </measure>
        </part>
        """, page.systems[1].part)
