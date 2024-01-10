import xml.etree.ElementTree as ET
from typing import List, Tuple


def split_part_to_systems(part: ET.Element) -> List[Tuple[Tuple[int, int], ET.Element]]:
    assert part.tag == "part"

    # TODO: add clefs and other things to the start of the measure

    systems: List[Tuple[Tuple[int, int], ET.Element]] = []
    
    page_index = 1
    system_index = 1
    system = ET.Element("part")
    system.attrib["id"] = part.attrib.get("id", "P1") \
        + "-" + str(page_index) + "-" + str(system_index)

    def yield_system():
        nonlocal system
        systems.append((
            (page_index, system_index), system
        ))
        system = ET.Element("part")
        system.attrib["id"] = part.attrib.get("id", "P1") \
            + "-" + str(page_index) + "-" + str(system_index)

    for measure in part:
        print_element = measure.find("print")
        if print_element is None:
            continue
        if print_element.attrib.get("new-system") == "yes":
            yield_system()
            system_index += 1
        if print_element.attrib.get("new-page") == "yes":
            yield_system()
            page_index += 1
            system_index = 1
        system.append(measure)
    yield_system()

    return systems