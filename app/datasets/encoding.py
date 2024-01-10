import xml.etree.ElementTree as ET
from typing import Iterable, Optional
import os
from .OpenScoreLiederMxlFile import OpenScoreLiederMxlFile
from app.symbolic.Mxl2Msq import Mxl2Msq


mxl = OpenScoreLiederMxlFile.load(
    "Chaminade,_Cécile/_/Alleluia",
    "6260992"
)
piano_part = mxl.get_piano_part()

processor = Mxl2Msq()
processor.process_part(piano_part)
