import xml.etree.ElementTree as ET
from typing import List, Optional
import copy


class System:
    def __init__(self):
        self.part = ET.Element("part")
    
    def append_measure(self, measure: ET.Element):
        assert measure.tag == "measure"
        self.part.append(measure)


class Page:
    def __init__(self):
        self.systems: List[System] = []
    
    def append_system(self, system: System):
        self.systems.append(system)


def split_part_to_systems(part: ET.Element, emit_explicit_header=True) -> List[Page]:
    assert part.tag == "part"

    pages: List[Page] = [Page()]
    page = pages[0]

    system = System()
    page.append_system(system)

    tracked_attributes = {
        "key": None, # Optional[ET.Element]
        "staves": 1, # int
        "clef": {} # Dict[int, ET.Element]
    }
    
    for original_measure in part:
        measure = copy.deepcopy(original_measure)

        new_system_measure = False
        print_element = measure.find("print")
        if print_element is not None:
            if print_element.attrib.get("new-system") == "yes":
                system = System()
                page.append_system(system)
                new_system_measure = True
            elif print_element.attrib.get("new-page") == "yes":
                page = Page()
                pages.append(page)
                system = System()
                page.append_system(system)
                new_system_measure = True
        
        head_attributes = _get_head_attributes(measure, create_if_missing=False)
        if head_attributes is not None:
            _update_tracked_attributes(tracked_attributes, head_attributes)
        if emit_explicit_header and new_system_measure and _something_is_tracked(tracked_attributes):
            head_attributes = _get_head_attributes(measure, create_if_missing=True)
            _emit_header(tracked_attributes, head_attributes)
        for attributes_element in measure.iterfind("attributes"):
            _update_tracked_attributes(tracked_attributes, attributes_element)
        system.append_measure(measure)

    return pages


def _get_head_attributes(measure: ET.Element, create_if_missing=False) -> Optional[ET.Element]:
    _IGNORE = {"print"}

    position = 0
    for i, child in enumerate(measure):
        position = i
        if child.tag in _IGNORE:
            continue
        elif child.tag == "attributes":
            return child
        else:
            # we hit a note/forward/backup or similar content
            break
    
    if create_if_missing:
        attributes_element = ET.Element("attributes")
        measure.insert(position, attributes_element)
        return attributes_element
    
    return None


def _update_tracked_attributes(tracked_attributes: dict, attributes: ET.Element):
    # key
    key_element = attributes.find("key")
    if key_element is not None:
        tracked_attributes["key"] = key_element
    
    # staves
    staves_element = attributes.find("staves")
    if staves_element is not None:
        staves = int(staves_element.text)
        assert staves > 0
        tracked_attributes["staves"] = staves
        clefs_to_clear = [
            s for s in tracked_attributes["clef"].keys()
            if s <= staves
        ]
        for s in clefs_to_clear:
            del tracked_attributes["clef"][s]

    # clefs
    for clef_element in attributes.findall("clef"):
        staff = int(clef_element.get("number", 1))
        assert staff > 0
        tracked_attributes["clef"][staff] = clef_element


def _emit_header(tracked_attributes: dict, attributes: ET.Element):
    # key
    key_element = attributes.find("key")
    if key_element is None and tracked_attributes["key"] is not None:
        attributes.append(
            copy.deepcopy(tracked_attributes["key"])
        )
    
    # clefs
    for number in sorted(tracked_attributes["clef"].keys()):
        try:
            _ = next(
                e for e in attributes.iterfind("clef")
                if e.get("number", "1") == str(number)
            )
        except StopIteration:
            # the clef element is not present, add it
            attributes.append(
                copy.deepcopy(tracked_attributes["clef"][number])
            )
    
    _sort_attributes(attributes)


def _something_is_tracked(tracked_attributes: dict) -> bool:
    if tracked_attributes["key"] is not None:
        return True
    if len(tracked_attributes["clef"]) > 0:
        return True
    return False


def _sort_attributes(attributes: ET.Element):
    tag_order = [
        # https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/attributes/
        "footnote", "level", "divisions", "key", "time", "staves",
        "part-symbol", "instruments", "clef", "staff-details", "transpose",
        "for-part", "directive", "measure-style"
    ]
    attributes[:] = sorted(
        attributes,
        key=lambda e: (tag_order.index(e.tag), e.get("number", "1"))
    )
