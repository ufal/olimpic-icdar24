import xml.etree.ElementTree as ET
from typing import List, Optional
import copy
from .sort_attributes import sort_attributes
from .get_head_attributes import get_head_attributes


class System:
    def __init__(self, part_id: Optional[str]):
        self.part = ET.Element("part")
        if part_id is not None:
            self.part.attrib["id"] = part_id
    
    def append_measure(self, measure: ET.Element):
        assert measure.tag == "measure"
        self.part.append(measure)


class Page:
    def __init__(self):
        self.systems: List[System] = []
    
    def append_system(self, system: System):
        self.systems.append(system)


def split_part_to_systems(
    part: ET.Element,
    emit_attributes_header=True,
    attributes_to_emit=["divisions", "key", "staves", "clef"],
    remove_page_and_system_breaks=True
) -> List[Page]:
    """
    Splits a MusicXML <part> element up into multiple <part> elements by
    system breaks and page breaks.

    part: Element
        The input <part> XML element
    
    emit_attributes_header: bool
        When true, the <attributes> element is added to the
        start of each system after splitting to make the resulting
        measures a valid MusicXML part.
    
    emit_attributes: list
        What <attributes> children to re-emit with each new system.
        The default contains clefs and key signature, which is typically
        present on each system in the music notation. It also contains
        divisions and staves, which is metadata useful for MusicXML completeness.
    
    remove_page_and_system_breaks: bool
        When true, the page and system breaks on the measures are removed.
    """
    assert part.tag == "part"
    part_id = part.get("id", None)

    pages: List[Page] = [Page()]
    page = pages[0]

    system = System(part_id)
    page.append_system(system)

    tracked_attributes = {
        "divisions": None, # Optional[ET.Element]
        "key": None, # Optional[ET.Element]
        "time": None, # Optional[ET.Element]
        "staves": None, # Optional[ET.Element]
        "clef": {} # Dict[int, ET.Element]
    }
    
    for original_measure in part:
        # make a copy so that we dont't modify the original
        measure = copy.deepcopy(original_measure)

        # detect page and system breaks
        new_system_measure = False
        print_element = measure.find("print")
        if print_element is not None:
            if print_element.get("new-system") == "yes":
                if remove_page_and_system_breaks:
                    del print_element.attrib["new-system"]
                system = System(part_id)
                page.append_system(system)
                new_system_measure = True
            elif print_element.get("new-page") == "yes":
                if remove_page_and_system_breaks:
                    del print_element.attrib["new-page"]
                page = Page()
                pages.append(page)
                system = System(part_id)
                page.append_system(system)
                new_system_measure = True
        
        # remove an empty print element
        if remove_page_and_system_breaks and print_element is not None:
            if len(print_element) == 0 and len(print_element.attrib) == 0:
                measure.remove(print_element)
        
        # emit the head attributes element
        head_attributes = get_head_attributes(measure, create_if_missing=False)
        if head_attributes is not None:
            _update_tracked_attributes(tracked_attributes, head_attributes)
        if emit_attributes_header and new_system_measure and _something_is_tracked(tracked_attributes):
            head_attributes = get_head_attributes(measure, create_if_missing=True)
            _emit_header(tracked_attributes, head_attributes, attributes_to_emit)
        for attributes_element in measure.iterfind("attributes"):
            _update_tracked_attributes(tracked_attributes, attributes_element)

        # the measure is processed
        system.append_measure(measure)

    return pages


def _update_tracked_attributes(tracked_attributes: dict, attributes: ET.Element):
    # divisions
    divisions_element = attributes.find("divisions")
    if divisions_element is not None:
        tracked_attributes["divisions"] = divisions_element
    
    # key
    key_element = attributes.find("key")
    if key_element is not None:
        tracked_attributes["key"] = key_element
    
    # time
    time_element = attributes.find("time")
    if time_element is not None:
        tracked_attributes["time"] = time_element
    
    # staves
    staves_element = attributes.find("staves")
    if staves_element is not None:
        staves = int(staves_element.text)
        assert staves > 0
        tracked_attributes["staves"] = staves_element
        clefs_to_clear = [
            s for s in tracked_attributes["clef"].keys()
            if s > staves
        ]
        for s in clefs_to_clear:
            del tracked_attributes["clef"][s]

    # clef
    for clef_element in attributes.findall("clef"):
        staff = int(clef_element.get("number", 1))
        assert staff > 0
        tracked_attributes["clef"][staff] = clef_element


def _emit_header(tracked_attributes: dict, attributes: ET.Element, attributes_to_emit: list):
    # divisions
    if "divisions" in attributes_to_emit:
        divisions_element = attributes.find("divisions")
        if divisions_element is None and tracked_attributes["divisions"] is not None:
            attributes.append(
                copy.deepcopy(tracked_attributes["divisions"])
            )
    
    # key
    if "key" in attributes_to_emit:
        key_element = attributes.find("key")
        if key_element is None and tracked_attributes["key"] is not None:
            attributes.append(
                copy.deepcopy(tracked_attributes["key"])
            )
    
    # time
    if "time" in attributes_to_emit:
        time_element = attributes.find("time")
        if time_element is None and tracked_attributes["time"] is not None:
            attributes.append(
                copy.deepcopy(tracked_attributes["time"])
            )
    
    # staves
    if "staves" in attributes_to_emit:
        staves_element = attributes.find("staves")
        if staves_element is None and tracked_attributes["staves"] is not None:
            attributes.append(
                copy.deepcopy(tracked_attributes["staves"])
            )
    
    # clef
    if "clef" in attributes_to_emit:
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
    
    sort_attributes(attributes)


def _something_is_tracked(tracked_attributes: dict) -> bool:
    if tracked_attributes["divisions"] is not None:
        return True
    if tracked_attributes["key"] is not None:
        return True
    if tracked_attributes["time"] is not None:
        return True
    if tracked_attributes["staves"] is not None:
        return True
    if len(tracked_attributes["clef"]) > 0:
        return True
    return False
