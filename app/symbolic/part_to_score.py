import xml.etree.ElementTree as ET


def part_to_score(
    part: ET.Element,
    part_id="P2",
    part_name="Piano",
    musicxml_version="3.1"
) -> ET.ElementTree:
    """Embeds a <part> element within a MusicXML <score-partwise> file"""
    
    root = ET.Element("score-partwise")
    root.attrib["version"] = musicxml_version

    part_list_element = ET.Element("part-list")
    score_part_element = ET.Element("score-part")
    score_part_element.attrib["id"] = part_id
    part_name_element = ET.Element("part-name")
    part_name_element.text = part_name
    score_part_element.append(part_name_element)
    part_list_element.append(score_part_element)

    root.append(part_list_element)

    part.attrib["id"] = part_id
    root.append(part)

    return ET.ElementTree(root)
