import xml.etree.ElementTree as ET
from typing import Optional, List, TextIO, Dict
import io
from .vocabulary import *


IGNORED_MEASURE_ELEMENTS = set([
    # https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/measure-partwise/
    "direction", "harmony", "figured-bass", "print", "sound", "listening",
    "grouping", "link", "bookmark"
])


class Linearizer:
    def __init__(self, errout: Optional[TextIO] = None):
        self._errout = errout or io.StringIO()
        """Print errors and warnings here"""

        self.output_tokens: List[str] = []
        """The output linearized sequence, split up into tokens"""
        
        # configuration
        # ...

        # within-part state
        self._page_index = 0 # page within part, zero-indexed
        self._system_index = 0 # system within page, zero-indexed
        self._divisions: Optional[int] = None # duration conversion
        self._beats_per_measure: Optional[int] = None # time signature top
        self._beat_type: Optional[int] = None # time signature bottom
        self._staves: Optional[int] = None # number of staves
        self._clefs: Dict[Optional[str], _Clef] = {} # clef for staves

        # within-measure state
        self._stem_orientation: Optional[str] = None # "up", "down", None
        self._staff: Optional[str] = None # "1", "2", None
        self._onset: int = 0 # in duration units
        self._voice: int = 0 # voice index in implicit numbering
        self._last_note_duration: Optional[int] = None # for chord checks

    def _error(self, *values):
        print(*values, file=self._errout)

    def _emit(self, token: str):
        """Emits a token into the output sequence"""
        assert token in ALL_TOKENS, f"Token '{token}' not in the vocabulary"
        self.output_tokens.append(token)

        # TODO: DEBUG PRINTING
        print(token)

    def process_part(self, part: ET.Element):
        # reset within-part state
        self._page_index = 0
        self._system_index = 0
        self._divisions = None
        self._beats_per_measure = None
        self._beat_type = None
        self._staves = None
        self._clefs = {}
        
        assert part.tag == "part"
        for measure in part:
            assert measure.tag == "measure"
            
            self.process_measure(measure)
    
    def process_measure(self, measure: ET.Element):
        # reset within-measure state
        self._stem_orientation = None
        self._staff = None
        self._onset = 0
        self._voice = 0
        self._last_note_duration = None

        self._handle_new_system_or_page(measure)
        
        # start a new measure
        self._emit("measure")

        for element in measure:
            if element.tag == "note":
                self.process_note(element)
            elif element.tag == "attributes":
                self.process_attributes(element)
            elif element.tag == "backup":
                self.process_backup(element, measure)
            elif element.tag == "forward":
                self.process_forward(element)
            elif element.tag in IGNORED_MEASURE_ELEMENTS:
                pass # ignored
            else:
                self._error("Unexpected measure element:", element, element.attrib)
    
    def _handle_new_system_or_page(self, measure: ET.Element):
        for element in measure:
            if element.tag == "print":
                if element.attrib.get("new-system") == "yes":
                    self._system_index += 1
                    return
                if element.attrib.get("new-page") == "yes":
                    self._page_index += 1
                    return
    
    def process_note(self, note: ET.Element):
        note_type = note.find("type")
        if note_type is not None:
            assert note_type.text in NOTE_TYPE_TOKENS
            self._emit(note_type.text)
        else:
            self._error("Note does not have <type>:", ET.tostring(note))

    def process_attributes(self, attributes: ET.Element):
        self._error("TODO: parse attributes")
        # self._divisions = int(element.find("divisions").text)
        # self._beats_per_measure = int(element.find("time/beats").text)
        # self._beat_type = int(element.find("time/beat-type").text)
        # assert element.find("staves").text == "2", "So far, only piano supported"
        # TODO: clefs
        self._error("TODO: clefs!")
    
    def process_backup(self, backup: ET.Element, measure: ET.Element):
        backup_duration = int(backup.find("duration").text)
        # print("\t", self._onset, backup_duration)
        # assert self._onset == backup_duration, "Backups can only be to measure start"
        if self._onset != backup_duration:
            self._error("Backups can only be to measure start", self._onset, backup_duration)
            self._error(self._page_index, self._system_index, measure.attrib.get("number"))
        # print("\t", "backup")
        self._emit("backup")
        # backup resets these values
        self._onset = 0
        self._staff = None
        self._stem_orientation = None

    def process_forward(self, forward: ET.Element):
        forward_duration = int(forward.find("duration").text)
        self._error("\t", self._onset, forward_duration)
        self._onset += forward_duration
        self._error("\t", "forward") # TODO: duration to type!!!
        self._emit("forward")


class _Clef:
    def __init__(self, staff: Optional[str], sign: str, line: str):
        self.staff = staff
        self.sign = sign
        self.line = line
