import xml.etree.ElementTree as ET
from typing import List, Optional, TextIO, Set
from .vocabulary import *
import io
from fractions import Fraction


MEASURE_ITEM_ROOTS = set([
    *NOTE_ROOT_TOKENS,
    "time",
    *KEY_TOKENS,
    *CLEF_TOKENS
])

MEASURE_ITEM_PREFIXES = set([
    *NOTE_PREFIX_TOKENS
])

MEASURE_ITEM_SUFFIXES = set([
    *NOTE_SUFFIX_TOKENS,
    *BEATS_TOKENS,
    *BEAT_TYPE_TOKENS
])

ATTRIBUTES_ROOTS = set([
    "time",
    *KEY_TOKENS,
    *CLEF_TOKENS
])


class Token:
    def __init__(self, terminal: str, position: int):
        self.terminal = terminal
        self.position = position


class Tree:
    def __init__(self, root: Token, prefixes: List[Token], suffixes: List[Token]):
        self.root = root
        self.prefixes = prefixes
        self.suffixes = suffixes


class Delinearizer:
    def __init__(self, errout: Optional[TextIO] = None):
        self._errout = errout or io.StringIO()
        """Print errors and warnings here"""

        self.part_element = ET.Element("part")

    def _error(self, token: Token, *values):
        header = f"[ERROR][Token '{token.terminal}' at position {token.position}]:"
        print(header, *values, file=self._errout)

    def process_text(self, text: str) -> ET.Element:
        tokens = self.lex(text)
        self.process_system(tokens)
        return self.part_element
    
    def lex(self, text: str) -> List[Token]:
        """Lexer phase that converts the input string to token sequence"""
        terminals = text.split()
        tokens = []
        for i, terminal in enumerate(terminals):
            position = i + 1
            token = Token(terminal, position)
            if terminal not in ALL_TOKENS:
                self._error(token, "Token not present in the vocabulary.")
                continue
            tokens.append(token)
        return tokens

    def process_system(self, tokens: List[Token]):
        """Takes all tokens produced by the recognition model"""
        measure_clusters = self.cluster_measures(tokens)
        for cluster_tokens in measure_clusters:
            self.process_measure(cluster_tokens)
        
        # TODO: replace fractional durations with actual durations and insert divisions
        # TODO: this will be part of the symbolic module, not this one
        # TODO: condition this by a setting in the constructor

        # TODO: add pitch adjustments due to accidentals - again a symbolic module function
    
    def cluster_measures(self, tokens: List[Token]) -> List[List[Token]]:
        clusters: List[List[Token]] = []

        this_cluster: List[Token] = []
        before_first_measure = True

        def _flush():
            nonlocal before_first_measure, clusters, this_cluster
            if not before_first_measure:
                clusters.append(this_cluster)
            elif len(this_cluster) > 0:
                self._error("There are tokens before the first 'measure' token.")

        for token in tokens:
            if token.terminal == "measure":
                _flush()
                this_cluster = []
                before_first_measure = False
                continue

            this_cluster.append(token)
        
        if len(this_cluster) > 0:
            _flush()
        
        return clusters

    def process_measure(self, tokens: List[Token]):
        """Takes tokens within a measure, without the measure token itself"""
        assert all(token.terminal != "measure" for token in tokens), \
            "Measure tokens should not contain the 'measure' token"

        measure_element = ET.Element("measure")
        attributes_element: Optional[ET.Element] = None

        trees = self.build_trees(tokens)
        for tree in trees:
            if tree.root.terminal in ATTRIBUTES_ROOTS:
                attributes_element_in = attributes_element
                attributes_element = self.process_attributes(
                    tree, attributes_element_in
                )
                if attributes_element_in is None:
                    measure_element.append(attributes_element)
            else:
                attributes_element = None
            
            if tree.root.terminal in NOTE_ROOT_TOKENS:
                notelike_element = self.process_notelike(tree)
                measure_element.append(notelike_element)
        
        # TODO: join neighboring forwards and backups

        self.part_element.append(measure_element)
    
    def build_trees(self, tokens: List[Token]) -> List[Tree]:
        trees: List[Tree] = []
        
        old_prefixes = [] # behind an already consumed root
        old_root = None # root that has been already consumed
        suffixes = [] # for a root that has already been consumed
        prefixes = [] # for a root to be consumed

        def _first_shift(current_root: Token):
            nonlocal trees, old_prefixes, prefixes, old_root, suffixes
            assert old_root is None
            for token in suffixes:
                self._error(token, "Dangling suffix token.")
            old_prefixes = prefixes
            old_root = current_root
            suffixes = []
            prefixes = []

        def _normal_shift(current_root: Token):
            nonlocal trees, old_prefixes, prefixes, old_root, suffixes
            assert old_root is not None
            trees.append(Tree(old_root, old_prefixes, suffixes))
            old_prefixes = prefixes
            old_root = current_root
            suffixes = []
            prefixes = []
        
        def _last_shift():
            nonlocal trees, old_prefixes, prefixes, old_root, suffixes
            if old_root is not None:
                trees.append(Tree(old_root, old_prefixes, suffixes))
            for token in prefixes:
                self._error(token, "Dangling prefix token.")

        for token in tokens:
            terminal = token.terminal

            if terminal in MEASURE_ITEM_PREFIXES:
                prefixes.append(token)
            elif terminal in MEASURE_ITEM_SUFFIXES:
                suffixes.append(token)
            elif terminal in MEASURE_ITEM_ROOTS:
                if old_root is None:
                    _first_shift(token)
                else:
                    _normal_shift(token)
            else:
                self._error(token, "Unexpected measure item type.")
        
        _last_shift()

        return trees
    
    def process_attributes(self, tree: Tree, attributes_element: Optional[ET.Element]) -> ET.Element:
        if attributes_element is None:
            attributes_element = ET.Element("attributes")
        
        if tree.root.terminal in KEY_TOKENS:
            key_element = self.process_key_signature(tree)
            attributes_element.append(key_element)
        elif tree.root.terminal == "time":
            time_element = self.process_time_signature(tree)
            attributes_element.append(time_element)
        elif tree.root.terminal in CLEF_TOKENS:
            clef_element = self.process_clef(tree)
            attributes_element.append(clef_element)
        else:
            raise Exception("Unknown attributes token: " + tree.root.terminal)
        
        return attributes_element
    
    def process_key_signature(self, tree: Tree) -> ET.Element:
        assert tree.root.terminal in KEY_TOKENS

        self._list_unexpected_valencies(tree)

        fifths: str = tree.root.terminal.split(":")[-1]

        key_element = ET.Element("key")
        fifths_element = ET.Element("fifths")
        fifths_element.text = fifths
        key_element.append(fifths_element)
        return key_element
    
    def process_time_signature(self, tree: Tree) -> ET.Element:
        assert tree.root.terminal == "time"

        beats_token = self._extract_suffix(tree, BEATS_TOKENS)
        beat_type_token = self._extract_suffix(tree, BEAT_TYPE_TOKENS)
        self._list_unexpected_valencies(tree)

        # defaults
        beats = "4"
        beat_type = "4"

        if beats_token is not None:
            beats = beats_token.terminal.split(":")[-1]
        else:
            self._error(tree.root, "Missing beats token from time signature.")
        
        if beat_type_token is not None:
            beat_type = beat_type_token.terminal.split(":")[-1]
        else:
            self._error(tree.root, "Missing beat type token from time signature.")
        
        time_element = ET.Element("time")
        beats_element = ET.Element("beats")
        beats_element.text = beats
        beat_type_element = ET.Element("beat-type")
        beat_type_element.text = beat_type
        time_element.append(beats_element)
        time_element.append(beat_type_element)

        return time_element

    def process_clef(self, tree: Tree) -> ET.Element:
        assert tree.root.terminal in CLEF_TOKENS

        staff_token = self._extract_suffix(tree, STAFF_TOKENS)
        self._list_unexpected_valencies(tree)
        
        sign, line = tree.root.terminal.split(":")[-1]
        
        clef_element = ET.Element("clef")
        sign_element = ET.Element("sign")
        sign_element.text = sign
        line_element = ET.Element("line")
        line_element.text = line
        clef_element.append(sign_element)
        clef_element.append(line_element)

        if staff_token is not None:
            staff_number = staff_token.terminal.split(":")[-1]
            clef_element.attrib["number"] = staff_number

        return clef_element

    def process_notelike(self, tree: Tree) -> ET.Element:
        assert tree.root.terminal in NOTE_ROOT_TOKENS

        backup_token = self._extract_prefix(tree, {"backup"})
        forward_token = self._extract_prefix(tree, {"forward"})

        if backup_token is not None:
            backup_element = ET.Element("backup")
            self.process_forward_backup(backup_element, tree)
            return backup_element
        
        if forward_token is not None:
            forward_element = ET.Element("forward")
            self.process_forward_backup(forward_element, tree)
            return forward_element

        return self.process_note(tree)
    
    def process_forward_backup(self, element: ET.Element, tree: Tree):
        assert tree.root.terminal in NOTE_ROOT_TOKENS

        note_type = tree.root.terminal
        if note_type == "rest:measure":
            self._error(tree.root, "Rest measure cannot be the root of a forward/backup element.")
            return # no duration element will be produced

        time_modification_token = self._extract_suffix(tree, TIME_MODIFICATION_TOKENS)
        self._list_unexpected_valencies(tree)

        if time_modification_token is not None:
            duration: str = self._get_fractional_duration(note_type, time_modification_token.terminal)
        else:
            duration: str = self._get_fractional_duration(note_type, None)
        
        duration_element = ET.Element("duration")
        duration_element.text = duration
        element.append(duration_element)
    
    def process_note(self, tree: Tree) -> ET.Element:
        assert tree.root.terminal in NOTE_ROOT_TOKENS

        # === parse the note tokens ====

        note_type = tree.root.terminal
        is_measure_rest = note_type == "rest:measure"
        if is_measure_rest:
            note_type = None

        no_print_token = self._extract_prefix(tree, {"print-object:no"})
        grace_token = self._extract_prefix(tree, {"grace"})
        grace_slash_token = self._extract_prefix(tree, {"grace:slash"})
        chord_token = self._extract_prefix(tree, {"chord"})
        rest_token = self._extract_prefix(tree, {"rest"})
        pitch_token = self._extract_prefix(tree, PITCH_TOKENS)
        voice_token = self._extract_prefix(tree, VOICE_TOKENS)
        # TODO ..........
        time_modification_token = self._extract_suffix(tree, TIME_MODIFICATION_TOKENS)
        # TODO ..........
        self._list_unexpected_valencies(tree)

        # === reconstruct the note element ====

        note_element = ET.Element("note")
        if no_print_token is not None:
            note_element.attrib["print-object"] = "no"
        
        # <grace>
        if grace_token is not None:
            grace_element = ET.Element("grace")
            if grace_slash_token is not None:
                grace_element.attrib["slash"] = "yes"
            note_element.append(grace_element)
        
        # <chord>
        if chord_token is not None:
            note_element.append(ET.Element("chord"))
        
        # <rest> or <pitch>
        if rest_token is not None:
            rest_element = ET.Element("rest")
            if is_measure_rest:
                rest_element.attrib["measure"] = "yes"
            note_element.append(rest_element)
        elif pitch_token is not None:
            step, octave = pitch_token.terminal
            pitch_element = ET.Element("pitch")
            step_element = ET.Element("step")
            step_element.text = step
            # <alter> element is added later in postprocessing
            octave_element = ET.Element("octave")
            octave_element.text = octave
            pitch_element.append(step_element)
            pitch_element.append(octave_element)
            note_element.append(pitch_element)
        
        # <voice>
        # TODO: use tracked state which is overriden by given voice tokens

        # TODO ..........

        return note_element
    
    def _get_fractional_duration(self, note_type: str, time_modification: Optional[str]) -> str:
        assert note_type in NOTE_TYPE_TOKENS
        if time_modification is not None:
            assert time_modification in TIME_MODIFICATION_TOKENS

        quarter_multiple = NOTE_TYPE_TO_QUARTER_MULTIPLE[note_type]

        if time_modification is not None:
            denominator, numerator = time_modification.split("in")
            modified_quarter_multiple = quarter_multiple * Fraction(int(numerator), int(denominator))
        else:
            modified_quarter_multiple = quarter_multiple
        
        return str(modified_quarter_multiple)
    
    def _extract_suffix(self, tree: Tree, terminals: Set[str]) -> Optional[Token]:
        target_token: Optional[Token] = None

        i = 0
        while i < len(tree.suffixes):
            token = tree.suffixes[i]
            if token.terminal in terminals:
                if target_token is None:
                    target_token = token
                else:
                    self._error(
                        token,
                        f"Additional suffix token '{token.terminal}' " + \
                            f"for the '{tree.root.terminal}' token."
                    )
                
                del tree.suffixes[i]
                i -= 1
            i += 1

        return target_token
    
    def _extract_prefix(self, tree: Tree, terminals: Set[str]) -> Optional[Token]:
        target_token: Optional[Token] = None

        i = len(tree.prefixes) - 1
        while i >= 0:
            token = tree.prefixes[i]
            if token.terminal in terminals:
                if target_token is None:
                    target_token = token
                else:
                    self._error(
                        token,
                        f"Additional prefix token for the '{tree.root.terminal}' token."
                    )
                
                del tree.prefixes[i]
            i -= 1

        return target_token
    
    def _list_unexpected_valencies(self, tree: Tree):
        for token in tree.prefixes:
            self._error(token, f"Unexpected prefix token for the '{tree.root.terminal}' token.")
        for token in tree.suffixes:
            self._error(token, f"Unexpected suffix token for the '{tree.root.terminal}' token.")
