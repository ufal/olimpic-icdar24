import xml.etree.ElementTree as ET
from typing import Optional, List, TextIO, Dict
import io
from .vocabulary import *
from fractions import Fraction


IGNORED_MEASURE_ELEMENTS = set([
    # https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/measure-partwise/
    "direction", "harmony", "figured-bass", "print", "sound", "listening",
    "grouping", "link", "bookmark"
])

IGNORED_ATTRIBUTES_ELEMENTS = set([
    # https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/attributes/
    "footnote", "level", "part-symbol", "instruments", "staff-details",
    "directive", "measure-style"
])


# NOTE: Use assert only for very major things. For everything else,
# use self._error, so that the code works fine with slightly unexpected input


class Linearizer:
    def __init__(self, errout: Optional[TextIO] = None):
        self._errout = errout or io.StringIO()
        """Print errors and warnings here"""

        self.output_tokens: List[List[List[str]]] = [
            [ # first page
                [] # first system of the first page
            ]
        ]
        """The output linearized sequence, split up into pages, systems, and tokens"""
        
        # configuration
        # ...

        # within-part state
        self._page_index = 0 # page within part, zero-indexed
        self._system_index = 0 # system within page, zero-indexed
        self._divisions: Optional[int] = None # time units per one quarter note
        self._beats_per_measure: Optional[int] = None # time signature top
        self._beat_type: Optional[int] = None # time signature bottom
        self._measure_duration: Optional[int] = None # time-units per measure
        self._staves: Optional[int] = None # number of staves
        self._clefs: Dict[Optional[str], _Clef] = {} # clef for staves

        # within-measure state
        self._stem_orientation: Optional[str] = None # "up", "down", None
        self._staff: Optional[str] = None # "1", "2", None
        self._onset: int = 0 # in duration units
        self._voice: int = 0 # voice index in implicit numbering
        self._previous_note_duration: Optional[int] = None # for chord checks
        self._previous_note_pitch: Optional[str] = None # for chord checks

    def _error(self, *values):
        print(*values, file=self._errout)

    def _emit(self, token: str):
        """Emits a token into the output sequence"""
        assert token in ALL_TOKENS, f"Token '{token}' not in the vocabulary"
        
        pages = self.output_tokens
        while len(pages) <= self._page_index:
            pages.append([])
        
        systems = pages[self._page_index]
        while len(systems) <= self._system_index:
            systems.append([])
        
        tokens = systems[self._system_index]
        tokens.append(token)

        # TODO: DEBUG PRINTING
        # print(token)

    def process_part(self, part: ET.Element):
        # reset within-part state
        self._page_index = 0
        self._system_index = 0
        self._divisions = None
        self._beats_per_measure = None
        self._beat_type = None
        self._measure_duration = None
        self._staves = None
        self._clefs = {}
        
        assert part.tag == "part"
        for measure in part:
            assert measure.tag == "measure"
            
            self.process_measure(measure)
    
    def process_measure(self, measure: ET.Element):
        assert measure.tag == "measure"

        # reset within-measure state
        self._stem_orientation = None
        self._staff = None
        self._onset = 0
        self._voice = 0
        self._previous_note_duration = None
        self._previous_note_pitch = None

        self._handle_new_system_or_page(measure)
        
        # start a new measure
        self._emit("measure")

        for element in measure:
            if element.tag == "note":
                self.process_note(element, measure)
            elif element.tag == "attributes":
                self.process_attributes(element)
            elif element.tag == "backup":
                # self.process_backup(element, measure)
                pass
            elif element.tag == "forward":
                # self.process_forward(element)
                pass
            elif element.tag in IGNORED_MEASURE_ELEMENTS:
                pass # ignored
            else:
                # TODO: DEBUG disabled temporarily (barlines spam now)
                pass
                # self._error("Unexpected <measure> element:", element, element.attrib)
    
    def _handle_new_system_or_page(self, measure: ET.Element):
        assert measure.tag == "measure"

        for element in measure:
            if element.tag == "print":
                if element.attrib.get("new-system") == "yes":
                    self._system_index += 1
                    return
                if element.attrib.get("new-page") == "yes":
                    self._page_index += 1
                    self._system_index = 0
                    return
    
    def process_note(self, note: ET.Element, measure: ET.Element):
        assert note.tag == "note"

        # print-object="no" attribute
        no_print_object = False
        if note.attrib.get("print-object") == "no":
            no_print_object = True
            # self._error("TODO: handle non-printing objects")

        # [grace]
        grace_element = note.find("grace")
        is_grace_note = grace_element is not None
        if is_grace_note:
            self._emit("grace")
            if grace_element.attrib.get("slash") == "yes":
                self._emit("grace:slash")
        
        # [chord]
        chord_element = note.find("chord")
        is_chord = chord_element is not None
        if is_chord:
            self._emit("chord")

        # [rest]
        rest_element = note.find("rest")

        # [rest] or [pitch]
        rest_element = note.find("rest")
        is_measure_rest = False
        pitch_token: Optional[str] = None
        if rest_element is not None:
            self._emit("rest")
            is_measure_rest = rest_element.attrib.get("measure") == "yes"
        else:
            pitch_element = note.find("pitch")
            pitch_token = pitch_element.find("step").text + pitch_element.find("octave").text
            assert pitch_token in PITCH_TOKENS, "Invalid pitch: " + pitch_token
            self._emit(pitch_token)
        
        # [type] or [rest:measure] - the ROOT of the [note] sequence
        type_element = note.find("type")
        if type_element is not None:
            assert type_element.text in NOTE_TYPE_TOKENS
            self._emit(type_element.text)
        elif is_measure_rest:
            self._emit("rest:measure")
        else:
            self._error("Note does not have <type>:", ET.tostring(note))

        # TODO: [dot]

        # TODO: [accidental]

        # [stem]
        # stem orientation is reset with each voice start
        # and then only changes are recorded
        # DOUBLE STEMS: are encoded as two notes in two voices,
        # this is what MuseScore produces and is reasonable
        # (even though MusicXML allows for "double" as a value here)
        stem_element = note.find("stem")
        if stem_element is not None:
            if stem_element.text not in ["up", "down", "none"]:
                self._error(
                    f"Unknown stem type '{stem_element.text}'.",
                    "Measure: " + str(measure.attrib),
                    ET.tostring(note)
                )
            else:
                if self._stem_orientation != stem_element.text:
                    self._emit("stem:" + stem_element.text)
                    self._stem_orientation = stem_element.text
        
        # extract duration
        duration_element = note.find("duration")
        duration: Optional[int] = None
        if duration_element is None and not is_grace_note:
            self._error("Note lacks duration:", ET.tostring(note))
            duration = int(duration_element.text)
            assert duration > 0

        # check assumptions about the linearization process
        self._verify_note_duration(duration, note, measure, is_measure_rest, is_grace_note)
        self._verify_chords(duration, pitch_token, is_chord, note, measure)

        # perform on-exit state changes
        self._previous_note_duration = duration
        self._previous_note_pitch = pitch_token
    
    def _verify_note_duration(
        self, duration: Optional[int], note: ET.Element, measure: ET.Element,
        is_measure_rest: bool, is_grace_note: bool
    ):
        if duration is None:
            return

        # verify for measure rests
        if is_measure_rest:
            # TODO: DEBUG disabled
            # if duration != self._measure_duration:
            #     self._error(
            #         "Measure rest does not have expected duration.",
            #         "Divisions: " + str(self._divisions),
            #         "Time signature: " + str(self._beats_per_measure) + "/" + str(self._beat_type),
            #         "Measure duration: " + str(self._measure_duration),
            #         "Measure: " + repr(measure.attrib),
            #         "Note: " + repr(note.attrib),
            #         ET.tostring(note)
            #     )
            return
        
        # TODO: triplets

        # verify for regular notes
        # TODO
    
    def _verify_chords(
        self, duration: Optional[int], pitch_token: Optional[str],
        is_chord: bool, note: ET.Element, measure: ET.Element
    ):
        if not is_chord:
            return
        
        # verify duration
        if duration != self._previous_note_duration:
            self._error(
                "Chord notes have varying duration.",
                "Measure: " + repr(measure.attrib),
                ET.tostring(note)
            )
        
        # verify pitch order
        previous_order = PITCH_TOKENS.index(self._previous_note_pitch)
        current_order = PITCH_TOKENS.index(pitch_token)
        if previous_order > current_order:
            self._error(
                "Chord notes must have ascending pitches.",
                "Measure: " + repr(measure.attrib),
                ET.tostring(note)
            )

    def process_attributes(self, attributes: ET.Element):
        # the order of elements is well defined
        # https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/attributes/
        assert attributes.tag == "attributes"

        for element in attributes:
            if element.tag == "divisions":
                self.process_divisions(element)
            elif element.tag == "key":
                pass # TODO
            elif element.tag == "time":
                self.process_time_signature(element)
            elif element.tag == "staves":
                pass # TODO
            elif element.tag == "clef":
                self.process_clef(element)
            elif element.tag in IGNORED_ATTRIBUTES_ELEMENTS:
                pass # ignored
            else:
                self._error("Unexpected <attributes> element:", element, element.attrib)

        # self._error("TODO: parse attributes")
        # self._divisions = int(element.find("divisions").text)
        # self._beats_per_measure = int(element.find("time/beats").text)
        # self._beat_type = int(element.find("time/beat-type").text)
        # assert element.find("staves").text == "2", "So far, only piano supported"
        # TODO: clefs
        # self._error("TODO: clefs!")

    def process_divisions(self, divisions: ET.Element):
        assert divisions.tag == "divisions"

        self._divisions = int(divisions.text)
        assert self._divisions > 0, "<divisions> should be a positive number"

    def process_time_signature(self, time: ET.Element):
        assert time.tag == "time"

        assert self._divisions is not None, "Time signature should follow <divisions>"
        
        beats_element = time.find("beats")
        assert beats_element is not None, "<beats> must be present in <time> element"
        beat_type_element = time.find("beat-type")
        assert beat_type_element is not None, "<beat-type> must be present in <time> element"
        
        self._beats_per_measure = int(beats_element.text)
        assert self._beats_per_measure > 0
        self._beat_type = int(beat_type_element.text)
        assert self._beat_type > 0

        # emit tokens
        self._emit("time")
        self._emit("beats:" + str(self._beats_per_measure))
        self._emit("beat-type:" + str(self._beat_type))

        # compute measure duration
        beat_type_fraction = Fraction(1, self._beat_type)
        quarters_per_beat_type = beat_type_fraction / Fraction(1, 4)
        quarters_per_measure = quarters_per_beat_type * self._beats_per_measure
        time_units_per_measure = quarters_per_measure * self._divisions
        assert time_units_per_measure.denominator == 1, "Measure duration calculation failed"
        self._measure_duration = time_units_per_measure.numerator
    
    def process_clef(self, clef: ET.Element):
        assert clef.tag == "clef"

        line_element = clef.find("line")
        assert line_element is not None, "<line> must be present in <clef> element"
        sign_element = clef.find("sign")
        assert sign_element is not None, "<sign> must be present in <clef> element"

        self._emit("clef:" + sign_element.text.upper() + line_element.text)
    
    def process_backup(self, backup: ET.Element, measure: ET.Element):
        assert backup.tag == "backup"

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
        assert forward.tag == "forward"

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
