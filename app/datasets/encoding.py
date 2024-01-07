import xml.etree.ElementTree as ET
from typing import Iterable
import os
from .OpenScoreLiederMxlFile import OpenScoreLiederMxlFile


class MusicXml2Sequence:
    """Stateful MXL file to sequence convertor"""
    def __init__(self):
        # within file state
        # (none)

        # within part state
        self._page_index = 0
        self._system_index = 0 # system within page

        # within measure state
        self._stem_orientation = None
        self._staff = 0
        self._voice = 0

    def process_part(self, measures: Iterable[ET.Element]):
        self._system_index = 0
        
        for measure in measures:
            assert measure.tag == "measure"
            
            self.process_measure(measure)
    
    def process_measure(self, measure: ET.Element):
        self._stem_orientation = None
        self._staff = 0
        self._voice = 0
        
        print(measure, measure.attrib)
        for element in measure:
            if element.tag == "note":
                self.process_note(element)
            elif element.tag == "print":
                if element.attrib.get("new-system") == "yes":
                    self._system_index += 1
                if element.attrib.get("new-page") == "yes":
                    self._page_index += 1
            elif element.tag == "direction":
                # we will ignore direction markings, too niche
                # (such as dynamics or pedals)
                # https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/direction-type/
                pass
            else:
                # TODO: throw exception
                print("\t", element, element.attrib)
    
    def process_note(self, note: ET.Element):
        # at the end we check there are no unused elements
        # (another words, we understand everthing we see)
        consumed_elements = set()

        # the token sequence representing the note
        seq = []

        # <chord>
        # chord (next chord note)
        chord = note.find("chord")
        if chord is not None:
            seq.append("chord")
            consumed_elements.add(chord)

        # <rest> / <pitch>
        # rest or pitch
        rest = note.find("rest")
        if rest is not None:
            seq.append("rest")
            consumed_elements.add(rest)
        else:
            pitch = note.find("pitch")
            pitch_value = pitch.find("step").text + pitch.find("octave").text
            seq.append(pitch_value)
            consumed_elements.add(pitch)

        # <duration>
        # actual temporal note duration is ignored
        consumed_elements.add(note.find("duration"))

        # <type>
        # note type (visual duration)
        seq.append(note.find("type").text)
        consumed_elements.add(note.find("type"))

        # <voice>
        # voices don't have explicit names in the sequence,
        # instead, voice changes are performed with <backups>
        consumed_elements.add(note.find("voice"))

        # <dot>
        for dot in note.findall("dot"):
            seq.append("dot")
            consumed_elements.add(dot)

        # TODO: accidentals

        # TODO: tuplets

        # <stem>
        # stem orientation is reset with each voice start
        # and then only changes are recorded
        # DOUBLE STEMS: are encoded as two notes in two voices,
        # this is what MuseScore produces and is reasonable
        # (even though MusicXML allows for "double" as a value here)
        stem = note.find("stem")
        if stem is not None:
            consumed_elements.add(stem)
            assert stem.text in ["up", "down"]
            if self._stem_orientation != stem.text:
                seq.append("stem:" + stem.text)
                self._stem_orientation = stem.text

        # <staff>
        # like stems, staves are indicated at the beginning
        # of a measure, voice, and during a change of staff
        staff = note.find("staff")
        consumed_elements.add(staff)
        assert staff.text in ["1", "2"]
        if self._staff != staff.text:
            seq.append("staff:" + staff.text)
            self._staff = staff.text

        print("\t\t", " ".join(seq))

        # check consumed elements
        for element in note:
            if element not in consumed_elements:
                # TODO: throw with unknown type
                print("\t\t", element)




mxl = OpenScoreLiederMxlFile.load(
    "Chaminade,_Cécile/_/Alleluia",
    "6260992"
)
piano_part = mxl.get_piano_part()

processor = MusicXml2Sequence()
processor.process_part(piano_part)
