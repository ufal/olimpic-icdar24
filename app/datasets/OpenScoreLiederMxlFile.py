import zipfile
import xml.etree.ElementTree as ET
import os
from typing import Iterable


class OpenScoreLiederMxlFile:
    def __init__(self, id: str, path: str, tree: ET.ElementTree):
        self.id = id
        self.path = path
        self.tree = tree

        # all MuseScore exported MusicXML files should be partwise organized
        # https://www.w3.org/2021/06/musicxml40/tutorial/structure-of-musicxml-files/
        assert tree.getroot().tag == "score-partwise"

    @staticmethod
    def load(directory_path: str, id: str) -> "OpenScoreLiederMxlFile":
        path = os.path.join(
            "datasets/OpenScore-Lieder/scores",
            directory_path,
            f"lc{id}.mxl"
        )
        with zipfile.ZipFile(path, "r") as archive:
            with archive.open(f"lc{id}.xml") as file:
                tree = ET.parse(file)
                return OpenScoreLiederMxlFile(id, path, tree)
    
    def resolve_piano_part_id(self) -> str:
        part_list = self.tree.getroot().find("part-list")
        for part in part_list.findall("score-part"):
            if part.find("score-instrument/instrument-name").text == "Piano":
                return part.attrib["id"]
        raise Exception(
            "No piano part found:\n" \
                + str(ET.tostring(part_list), "utf-8")
        )
    
    def get_piano_part(self) -> Iterable[ET.Element]:
        part_id = self.resolve_piano_part_id()

        parts = [
            part for part in self.tree.findall("part")
            if part.attrib["id"] == part_id
        ]
        assert len(parts) == 1
        part = parts[0]

        return part
