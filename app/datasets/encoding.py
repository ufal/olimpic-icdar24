import xml.etree.ElementTree as ET
from typing import Iterable, Optional
import os
from .OpenScoreLiederMxlFile import OpenScoreLiederMxlFile


class MusicXml2Sequence:
    """Stateful MXL file to sequence convertor"""
    def __init__(self):
        # within file state
        # (none)

        # within part state
        self._divisions: Optional[int] = None
        self._beats_per_measure: Optional[int] = None
        self._beat_type: Optional[int] = None
        self._page_index = 0
        self._system_index = 0 # system within page

        # within measure state
        self._stem_orientation: Optional[str] = None
        self._staff: Optional[str] = None
        self._onset = 0 # in duration units
        self._voice = 0
        self._last_note_duration: Optional[int] = None # for chord checks

    def process_part(self, measures: Iterable[ET.Element]):
        self._system_index = 0
        
        for measure in measures:
            assert measure.tag == "measure"
            
            self.process_measure(measure)
    
    def process_measure(self, measure: ET.Element):
        self._stem_orientation = None
        self._staff = None
        self._onset = 0
        self._voice = 0
        self._last_note_duration = None
        
        print(measure, measure.attrib)
        for element in measure:
            if element.tag == "note":
                self.process_note(element)
            elif element.tag == "print":
                if element.attrib.get("new-system") == "yes":
                    self._system_index += 1
                if element.attrib.get("new-page") == "yes":
                    self._page_index += 1
            elif element.tag == "attributes":
                self._divisions = int(element.find("divisions").text)
                self._beats_per_measure = int(element.find("time/beats").text)
                self._beat_type = int(element.find("time/beat-type").text)
                assert element.find("staves").text == "2", "So far, only piano supported"
                # TODO: clefs
                print("TODO: clefs!")
            elif element.tag == "backup":
                backup_duration = int(element.find("duration").text)
                # print("\t", self._onset, backup_duration)
                assert self._onset == backup_duration, "Backups can only be to measure start"
                print("\t", "backup")
                # backup resets these values
                self._onset = 0
                self._staff = None
                self._stem_orientation = None
            elif element.tag == "forward":
                forward_duration = int(element.find("duration").text)
                print("\t", self._onset, forward_duration)
                self._onset += forward_duration
                print("\t", "forward") # TODO: duration to type!!!
            elif element.tag == "direction":
                # we will ignore direction markings, too niche
                # (such as dynamics, text, or pedals)
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

        # <grace>
        grace = note.find("grace")
        if grace is not None:
            seq.append("grace")
            consumed_elements.add(grace)

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
        duration = note.find("duration")
        if duration is None:
            assert grace is not None, "Non-duration notes must be grace notes"
        elif chord is not None:
            assert self._last_note_duration is not None, \
                "Chord extension note may not be the first note in a measure"
            assert self._last_note_duration == int(duration.text), \
                "Chord notes must have the same duration"
        else:
            self._onset += int(duration.text)
            self._last_note_duration = int(duration.text)
        consumed_elements.add(duration)

        # <tie>
        # tie is an audio information, notation/tied is the graphical one
        consumed_elements.add(note.find("tie"))

        # <voice>
        # voices don't have explicit names in the sequence,
        # instead, voice changes are performed with <backups>
        consumed_elements.add(note.find("voice"))

        # <type>
        # note type (visual duration)
        seq.append(note.find("type").text)
        consumed_elements.add(note.find("type"))

        # <dot>
        for dot in note.findall("dot"):
            seq.append("dot")
            consumed_elements.add(dot)

        # <accidental>
        accidental = note.find("accidental")
        if accidental is not None:
            consumed_elements.add(accidental)
            assert accidental.text in ["sharp", "flat", "natural"]
            seq.append(accidental.text)

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

        # <beam>
        for beam in note.findall("beam"):
            assert beam.text in ["begin", "end", "continue"]
            if beam.text != "continue":
                seq.append("beam:" + beam.text)
            consumed_elements.add(beam)

        # print("\t\t", " ".join(seq))

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
