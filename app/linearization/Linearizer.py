import xml.etree.ElementTree as ET
from typing import Iterator, Optional, List, TextIO, Dict
import io
from .vocabulary import *
from fractions import Fraction


IGNORED_MEASURE_ELEMENTS = set([
    # https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/measure-partwise/
    "direction", "harmony", "figured-bass", "print", "sound", "listening",
    "grouping", "link", "bookmark", "barline"
])

IGNORED_ATTRIBUTES_ELEMENTS = set([
    # https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/attributes/
    "footnote", "level", "part-symbol", "instruments", "staff-details",
    "directive", "measure-style"
])


# NOTE: Use assert only for very major things. For everything else,
# use self._error, so that the code works fine with slightly unexpected input


class Linearizer:
    def __init__(self, errout: Optional[TextIO] = None, fail_on_unknown_tokens=True):
        self._errout = errout or io.StringIO()
        """Print errors and warnings here"""

        self.output_tokens: List[str] = []
        """The output linearized sequence, split up into tokens"""

        self.fail_on_unknown_tokens = fail_on_unknown_tokens
        
        # within-part state
        self._part_id: Optional[str] = None # current part ID
        self._measure_number: Optional[str] = None # current measure number
        self._divisions: Optional[int] = None # time units per one quarter note
        self._beats_per_measure: Optional[int] = None # time signature top
        self._beat_type: Optional[int] = None # time signature bottom
        self._measure_duration: Optional[int] = None # time-units per measure
        self._staves: Optional[int] = None # number of staves
        self._clefs: Dict[int, str] = {} # clef tokens for staves
        self._key_signature_fifths: Optional[int] = None # key signature

        # within-measure state
        self._stem_orientation: Optional[str] = None # "up", "down", None
        self._staff: Optional[str] = None # "1", "2", None
        self._onset: int = 0 # in duration units
        self._voice: Optional[str] = None # "1", "2", ... "8", None
        self._previous_note_duration: Optional[int] = None # for chord checks
        self._previous_note_pitch: Optional[str] = None # for chord checks

    def _error(self, *values):
        header = f"[ERROR][P:{self._part_id} M:{self._measure_number}]:"
        print(header, *values, file=self._errout)

    def _emit(self, token: str):
        """Emits a token into the output sequence"""
        if self.fail_on_unknown_tokens:
            assert token in ALL_TOKENS, f"Token '{token}' not in the vocabulary"
        else:
            if token not in ALL_TOKENS:
                self._error(f"Token '{token}' not in the vocabulary")
                return
        
        self.output_tokens.append(token)

    def process_part(self, part: ET.Element):
        # reset within-part state
        self._part_id = None
        self._measure_number = None
        self._divisions = None
        self._beats_per_measure = None
        self._beat_type = None
        self._measure_duration = None
        self._staves = None
        self._clefs = {}
        self._key_signature_fifths = None
        
        assert part.tag == "part"
        self._part_id = part.attrib.get("id")
        for measure in part:
            if measure.tag is ET.Comment:
                continue # ignore comments

            assert measure.tag == "measure"
            
            self.process_measure(measure)
    
    def process_measure(self, measure: ET.Element):
        assert measure.tag == "measure"

        # reset within-measure state
        self._stem_orientation = None
        self._staff = None
        self._onset = 0
        self._voice = None
        self._previous_note_duration = None
        self._previous_note_pitch = None

        self._measure_number = measure.attrib.get("number")
        
        # start a new measure
        self._emit("measure")

        for element in measure:
            if element.tag in IGNORED_MEASURE_ELEMENTS:
                continue
            elif element.tag == "note":
                self.process_note(element, measure)
            elif element.tag == "attributes":
                self.process_attributes(element)
            elif element.tag == "backup":
                self.process_backup(element, measure)
            elif element.tag == "forward":
                self.process_forward(element)
            else:
                self._error("Unexpected <measure> element:", element, element.attrib)
    
    def process_note(self, note: ET.Element, measure: ET.Element):
        assert note.tag == "note"

        # [print-object:no]
        if note.attrib.get("print-object") == "no":
            self._emit("print-object:no")

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
        
        # [voice]
        voice_element = note.find("voice")
        if voice_element is not None:
            if self._voice != voice_element.text:
                self._emit("voice:" + voice_element.text)
                self._voice = voice_element.text
        
        # [type] or [rest:measure] - the ROOT of the [note] sequence
        type_element = note.find("type")
        if type_element is not None:
            assert type_element.text in NOTE_TYPE_TOKENS
            self._emit(type_element.text)
        elif is_measure_rest:
            self._emit("rest:measure")
        else:
            self._error("Note does not have <type>:", ET.tostring(note))
        
        # [time-modification] (tuplets rhythm-wise)
        if note.find("time-modification") is not None:
            actual = note.find("time-modification/actual-notes").text
            normal = note.find("time-modification/normal-notes").text
            token = actual + "in" + normal
            self._emit(token)

        # [dot]
        for dot_element in note.findall("dot"):
            self._emit("dot")

        # [accidental]
        accidental_element = note.find("accidental")
        if accidental_element is not None:
            accidental = accidental_element.text
            if accidental not in ACCIDENTAL_TOKENS:
                self._error("Unsupported accidental type:", accidental)
            self._emit(accidental)

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
                    ET.tostring(note)
                )
            else:
                if self._stem_orientation != stem_element.text:
                    self._emit("stem:" + stem_element.text)
                    self._stem_orientation = stem_element.text
        
        # [staff]
        # like stems, staves are indicated at the beginning
        # of a measure, voice, and during a change of staff
        staff_element = note.find("staff")
        if staff_element is not None:
            if staff_element.text not in ["1", "2", "3"]:
                self._error("Only staves 1,2,3 are supported.")
            else:
                assert self._staves >= 2
                if self._staff != staff_element.text:
                    self._emit("staff:" + staff_element.text)
                    self._staff = staff_element.text

        # [beam]
        for beam in note.findall("beam"):
            assert beam.text in ["begin", "end", "continue", "forward hook", "backward hook"]
            if beam.text != "continue":
                if beam.text == "forward hook":
                    self._emit("beam:forward-hook")
                elif beam.text == "backward hook":
                    self._emit("beam:backward-hook")
                else:
                    self._emit("beam:" + beam.text)

        # [tied]
        for tied_element in note.findall("notations/tied"):
            tied_type = tied_element.attrib.get("type")
            assert tied_type in ["start", "stop"]
            self._emit("tied:" + tied_type)

        # [tuplet]
        for tuplet_element in note.findall("notations/tuplet"):
            tuplet_type = tuplet_element.attrib.get("type")
            assert tuplet_type in ["start", "stop"]
            self._emit("tuplet:" + tuplet_type)
        
        # extended notations and ornaments
        self._process_extended_notations(note)
        
        # extract duration
        duration_element = note.find("duration")
        duration: Optional[int] = None
        if duration_element is None and not is_grace_note:
            self._error("Note lacks duration:", ET.tostring(note))
        elif duration_element is not None:
            duration = int(duration_element.text)
            assert duration > 0

        # check assumptions about the linearization process
        self._verify_note_duration(duration, note, measure, is_measure_rest, is_grace_note)
        self._verify_chords(duration, pitch_token, is_chord, note, measure)

        # perform on-exit state changes
        self._previous_note_duration = duration
        self._previous_note_pitch = pitch_token
        if duration is not None and not is_chord:
            self._onset += duration
    
    def _process_extended_notations(self, note: ET.Element):
        # save some compute time
        notations = note.find("notations")
        if notations is None:
            return

        # [slur]
        for slur_element in notations.findall("slur"):
            slur_type = slur_element.attrib.get("type")
            if slur_type == "continue":
                pass # ignore
            else:
                assert slur_type in ["start", "stop"]
                self._emit("slur:" + slur_type)

        # [fermata]
        fermata_element = notations.find("fermata")
        if fermata_element is not None:
            self._emit("fermata")

        # [arpeggiate]
        arpeggiate_element = notations.find("arpeggiate")
        if arpeggiate_element is not None:
            self._emit("arpeggiate")
        
        # [staccato]
        staccato_element = notations.find("articulations/staccato")
        if staccato_element is not None:
            self._emit("staccato")

        # [accent]
        accent_element = notations.find("articulations/accent")
        if accent_element is not None:
            self._emit("accent")

        # [strong-accent]
        strong_accent_element = notations.find("articulations/strong-accent")
        if strong_accent_element is not None:
            self._emit("strong-accent")

        # [tenuto]
        tenuto_element = notations.find("articulations/tenuto")
        if tenuto_element is not None:
            self._emit("tenuto")
        
        # [tremolo]
        tremolo_element = notations.find("ornaments/tremolo")
        if tremolo_element is not None:
            tremolo_type = tremolo_element.attrib.get("type", "single")
            tremolo_marks = tremolo_element.text
            assert tremolo_type in ["single", "start", "stop", "unmeasured"]
            assert tremolo_marks in ["1", "2", "3", "4"]
            self._emit("tremolo:" + tremolo_type)
            self._emit("tremolo:" + tremolo_marks)

        # [trill-mark]
        trill_mark_element = notations.find("ornaments/trill-mark")
        if trill_mark_element is not None:
            self._emit("trill-mark")
    
    def _verify_note_duration(
        self, duration: Optional[int], note: ET.Element, measure: ET.Element,
        is_measure_rest: bool, is_grace_note: bool
    ):
        if duration is None:
            return

        # verify for measure rests
        if is_measure_rest:
            if duration != self._measure_duration:
                self._error(
                    "Measure rest does not have expected duration.",
                    "Divisions:", + self._divisions,
                    "Measure duration:", self._measure_duration,
                    ET.tostring(note)
                )
            return
        
        # verify for regular notes
        expected_duration, expected_duration_float = self._expected_note_duration(note)
        if expected_duration != duration:
            self._error(
                "Note does not have expected duration.",
                "Expected:", expected_duration_float,
                "Actual:", duration,
                ET.tostring(note)
            )
    
    def _expected_note_duration(self, note: ET.Element) -> int:
        type_element = note.find("type")
        note_type = type_element.text

        # simple conversion
        expected_duration: Fraction = NOTE_TYPE_TO_QUARTER_MULTIPLE[note_type] * self._divisions

        # handle duration dots
        dot_duration = expected_duration / 2
        for _ in note.findall("dot"):
            expected_duration += dot_duration
            dot_duration /= 2
        
        # handle time modification
        if note.find("time-modification") is not None:
            actual = int(note.find("time-modification/actual-notes").text)
            normal = int(note.find("time-modification/normal-notes").text)
            expected_duration *= Fraction(normal, actual)
        
        # The denominaotor now SHOULD be 1, if the file is valid MusicXML.
        # BUT! The reality strucks and you find out that MuseScore caps
        # divisions at 480 and won't go higher. Which causes non-integer
        # results here. And they don't even covnert to int, they round instead!
        # So there must have been some obscure reason for their decision.
        # Either they play 4D Chess, or some random contributor on the internet
        # put round() there because he felt like so. Either way, we have to
        # round as well to get the same results.
        return round(expected_duration), float(expected_duration) # keep the floats for error handling
        # assert expected_duration.denominator == 1
        # return expected_duration.numerator
    
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
                ET.tostring(note)
            )
        
        # verify pitch order
        previous_order = PITCH_TOKENS.index(self._previous_note_pitch)
        current_order = PITCH_TOKENS.index(pitch_token)
        if previous_order > current_order:
            self._error(
                "Chord notes must have ascending pitches.",
                ET.tostring(note)
            )

    def process_attributes(self, attributes: ET.Element):
        # the order of elements is well defined
        # https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/attributes/
        assert attributes.tag == "attributes"

        # divisions
        divisions_element = attributes.find("divisions")
        if divisions_element is not None:
            self.process_divisions(divisions_element)
        
        # key signature (process even if missing due to re-prints)
        key_element = attributes.find("key")
        self.process_key_signature(key_element)

        # time signature
        time_element = attributes.find("time")
        if time_element is not None:
            self.process_time_signature(time_element)
        
        # staves
        staves_element = attributes.find("staves")
        if staves_element is not None:
            self._staves = int(staves_element.text)

        # clef (process even if missing due to re-prints)
        clef_elements = attributes.findall("clef")
        self.process_clefs(clef_elements)

        # check that all elements have been processed
        for element in attributes:
            if element.tag in ["divisions", "key", "time", "staves", "clef"]:
                pass # has been processed already
            elif element.tag in IGNORED_ATTRIBUTES_ELEMENTS:
                pass # ignored
            else:
                self._error("Unexpected <attributes> element:", element, element.attrib)

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

    def process_key_signature(self, key: Optional[ET.Element]):
        if key is not None:
            self._key_signature_fifths = int(key.find("fifths").text)
            self._emit("key:fifths:" + str(self._key_signature_fifths))
    
    def process_clefs(self, clefs: List[ET.Element]):
        # get all the currently defined clefs (staff -> clef token)
        # (those are always printed)
        clefs_to_print = {}
        for clef in clefs:
            staff_number = int(clef.attrib.get("number", "1"))
            clef_token = (
                "clef:" + clef.find("sign").text.upper()
                    + clef.find("line").text
            )
            clefs_to_print[staff_number] = clef_token

            # remember the clef for future printing
            self._clefs[staff_number] = clef_token

        # now we can print all the clefs to be printed, IN THE PROPER ORDER
        for staff_number in sorted(clefs_to_print.keys()):
            self._emit(clefs_to_print[staff_number])
            if self._staves is not None: # emit staff number only if we're multistaff
                self._emit("staff:" + str(staff_number))
    
    def process_backup(self, backup: ET.Element, measure: ET.Element):
        assert backup.tag == "backup"

        # get the duration
        backup_duration = int(backup.find("duration").text)
        assert backup_duration > 0

        # build up to match the duration
        for note_type in self._duration_to_note_types(backup_duration):
            self._emit("backup")
            self._emit(note_type)
        
        # backup resets these values
        self._voice = None
        self._onset -= backup_duration
        self._staff = None
        self._stem_orientation = None

    def process_forward(self, forward: ET.Element):
        assert forward.tag == "forward"

        # get the duration
        forward_duration = int(forward.find("duration").text)
        assert forward_duration > 0

        # build up to match the duration
        for note_type in self._duration_to_note_types(forward_duration):
            self._emit("forward")
            self._emit(note_type)

        # update within-measure onset
        self._onset += forward_duration
    
    def _duration_to_note_types(self, duration: int) -> Iterator[str]:
        assert self._divisions is not None, "<backup/forward> should follow <divisions>"
        assert NOTE_TYPE_TOKENS[-1] == "maxima"
        
        remainder = duration
        step = self._divisions * 32 # 32 quarters in one maxima
        
        for note_type in reversed(NOTE_TYPE_TOKENS):
            if remainder <= 0:
                break
            if step <= remainder:
                yield note_type
                remainder -= step
            step //= 2
        
        # Happens in very few, very weird cases
        if remainder != 0:
            self._error(
                # possible solution: make the forward a tuplet note
                "Duration could not be split up to note types for " + \
                "forward/backup. This is most likely a tuplet forward.",
                "Duration:", duration,
                "Divisions:", self._divisions
            )
