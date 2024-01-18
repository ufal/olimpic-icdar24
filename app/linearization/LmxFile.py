from typing import List
from .vocabulary import *


LMX_FILE_VERSION = "1.0"


class LmxFile:
    """Represents a Linearized MusicXML file in memory"""
    def __init__(self):
        self.systems: List[List[str]] = []
        "A list of token sequences, one for each system"

        self.extended_flavor = False
        "Does the file use extended flavor or only the core flavor"

    @staticmethod
    def load(path: str) -> "LmxFile":
        """Loads Linearized MusicXML from a file"""
        lmx = LmxFile()

        in_header = True
        with open(path, "r") as file:
            for line in file:
                comment_start = line.find("#")
                if comment_start >= 0:
                    line = line[:comment_start] + "\n"

                if in_header:
                    if line.strip() == "---":
                        in_header = False
                        lmx.systems.append([])
                        continue
                    lmx._load_header_line(line)
                    continue
                
                if line.strip() == "---":
                    lmx.systems.append([])
                    continue
                
                lmx._load_system_line(line)
        
        return lmx
    
    def _load_header_line(self, line: str):
        field, value = line.strip().split(": ")
        if field == "version":
            if value != LMX_FILE_VERSION:
                raise Exception("Loaded file has unsupported version")
        elif field == "flavor":
            self.extended_flavor = value == "extended"

    def _load_system_line(self, line: str):
        tokens = line.strip().split()
        for token in tokens:
            if token not in ALL_TOKENS:
                raise Exception(f"Unknown token '{token}' in the LMX file")
            self.systems[-1].append(token)
