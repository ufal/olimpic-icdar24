import glob
import os
import sys
import xml.etree.ElementTree as ET
from ...linearization.Linearizer import Linearizer
from ...symbolic.part_to_score import part_to_score
from ..config import GRANDSTAFF_DATASET_PATH, MSCORE
import music21
import tempfile
import json
from typing import List


def build(
    slice_index: int,
    slice_count: int,
    soft: bool
):
    # load files to parse
    paths = glob.glob(
        os.path.join(GRANDSTAFF_DATASET_PATH, "**/*.krn"),
        recursive=True
    )
    paths = list(sorted(path[:-len(".krn")] for path in paths))
    paths = _slice_paths(paths, slice_index, slice_count)
    print(f"Loaded {len(paths)} paths to convert, slice {slice_index}/{slice_count}")

    _kern_to_crude_musicxml(paths, soft)
    _refine_musicxml_via_musescore(paths, soft)
    _finalize_lmx_and_musicxml_annotations(paths)


def _slice_paths(paths: list, slice_index: int, slice_count: int):
    """Take a specific slice from the given paths"""
    assert slice_index >= 0
    assert slice_index < slice_count
    
    slice_size = len(paths) // slice_count
    
    slice_paths = paths[
        (slice_index * slice_size) : ((slice_index + 1) * slice_size)
    ]
    if slice_index == slice_count - 1:
        slice_paths = paths[(slice_index * slice_size):]
    
    return slice_paths


def _kern_to_crude_musicxml(base_paths: List[str], soft: bool):
    for i, base_path in enumerate(base_paths):
        if soft:
            if os.path.exists(base_path + ".crude.musicxml"):
                continue

        print(f"Kern to crude musicxml:", base_path)

        # load the kern score into music21
        # (via the low-level converter API)
        converter = music21.converter.subConverters.ConverterHumdrum()
        kern_data = _load_kern_file(base_path + ".krn")
        converter.parseData(kern_data)
        score = converter.stream

        # replaces parts with "PartStaff" so that MusicXML exported
        # serializes the piano staff-parts properly into one part
        parts = list(score.parts)
        assert len(parts) == 2, f"Invalid number of parts @ {base_path}"

        piano_parts = []
        for part in parts:
            score.remove(part)
            piano_part = music21.stream.PartStaff()
            piano_part.append(list(part))
            score.append(piano_part)
            piano_parts.append(piano_part)

        # and add a staff group, that's also needed for the convertor
        staff_group = music21.layout.StaffGroup(
            piano_parts, name="Piano", abbreviation="Pno.", symbol="brace"
        )
        score.insert(0, staff_group)

        # a sanity check
        if not score.isWellFormedNotation():
            print("[ERROR] Score is not a well formed notation.", "@", base_path)
            continue

        # now, use the musicxml exporter in music21
        exporter = music21.musicxml.m21ToXml.ScoreExporter(score)
        root = exporter.parse()

        # more sanity checks
        if len(root.findall("part")) != 1:
            print("[ERROR] Invalid part count in the crude MusicXML.", "@", base_path)
        
        # give the part a name (the values in the StaffGroup are ignored)
        part_name_element = root.find("part-list/score-part/part-name")
        part_name_element.text = "Piano"

        # write to file
        xml_string = str(ET.tostring(
            root,
            encoding="utf-8",
            xml_declaration=True
        ), "utf-8")
        with open(base_path + ".crude.musicxml", "w") as file:
            file.write(xml_string)


def _load_kern_file(path: str) -> str:
    with open(path) as file:
        lines = file.readlines()
    
    # Chop-short kern files where the two piano spines merge into one spine.
    # These occur like 80 times in the whole dataset, and they crash
    # the music21 ConverterHumdrum. They even cause trouble to Verovio,
    # as you can see the images lack any notes after the merger. So we
    # decided to treat it in accordance with what is seen in those images
    # and crop the LMX and MusicXML annotations short.
    #
    # You can check out these examples:
    # - beethoven/piano-sonatas/sonata07-3/original_m-20-25
    # - beethoven/piano-sonatas/sonata07-3/original_m-30-35
    # - beethoven/piano-sonatas/sonata07-3/original_m-35-40
    # - beethoven/piano-sonatas/sonata15-1/original_m-445-449
    # - chopin/mazurkas/mazurka41-2/original_m-66-71
    # - joplin/joplin/pleasant/original_m-41-46
    # - joplin/joplin/pleasant/original_m-81-86
    #
    chop_score_at = None
    for i, line in enumerate(lines):
        if line == "*v\t*v\n": # merger of the last two spines
            chop_score_at = i
            break
    if chop_score_at is not None:
        lines = lines[0:chop_score_at] # chop to just before the spine merger
        lines.append("=\t=\n") # measure end
        lines.append("*-\t*-\n") # score end

    return "".join(lines) # each line already contains "\n"


def _refine_musicxml_via_musescore(base_paths: List[str], soft: bool):
    """We feed the crude musicxml files through musescore to normalize voice numbers,
    measure numbers, part IDs, etc. - to get the "canonical" MusicXML document."""

    # create the conversion json file
    print(f"Preparing musescore batch file...")
    conversion = []
    for base_path in base_paths:
        if soft:
            if os.path.exists(base_path + ".musescore.musicxml"):
                continue
        conversion.append({
            "in": base_path + ".crude.musicxml",
            "out": base_path + ".musescore.musicxml"
        })
    
    if len(conversion) == 0:
        return

    # run musescore conversion
    tmp = tempfile.NamedTemporaryFile(mode="w", delete=False)
    try:
        json.dump(conversion, tmp)
        tmp.close()

        assert os.system(
            f"{MSCORE} -j \"{tmp.name}\""
        ) == 0
    finally:
        tmp.close()
        os.unlink(tmp.name)


def _finalize_lmx_and_musicxml_annotations(base_paths: List[str]):
    for base_path in base_paths:
        print(f"Finalizing annotations:", base_path)

        with open(base_path + ".musescore.musicxml") as file:
            tree = ET.parse(file)
        
        # should be the case, there was a check before
        assert len(tree.getroot().findall("part")) == 1

        # extract the part element
        part = tree.getroot().find("part")

        # produce the LMX annotation
        linearizer = Linearizer(
            errout=sys.stdout,
            fail_on_unknown_tokens=False # ignore OOV tokens
        )
        linearizer.process_part(part)
        lmx_string = " ".join(linearizer.output_tokens)
        with open(base_path + ".lmx", "w") as file:
            file.write(lmx_string + "\n")

        # produce the MusicXML annotation
        score = part_to_score(part)
        xml_string = str(ET.tostring(
            score.getroot(),
            encoding="utf-8",
            xml_declaration=True
        ), "utf-8")
        with open(base_path + ".musicxml", "w") as file:
            file.write(xml_string)
        
        # clean up temporary files
        os.unlink(base_path + ".crude.musicxml")
        os.unlink(base_path + ".musescore.musicxml")
