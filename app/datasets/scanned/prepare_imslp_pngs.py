import glob
import os
import re
from ..config import SCANNED_DATASET_PATH


def prepare_imslp_pngs():

    print("Preparing IMSLP PNGs...")

    # get the set of IMSLP IDs without the hash symbol
    downloaded_pdfs = glob.glob(f"{SCANNED_DATASET_PATH}/imslp_pdfs/*.pdf")
    imslp_ids = set(
        re.match("^IMSLP(\d+)", os.path.basename(path))[1]
        for path in downloaded_pdfs
    )

    for id in imslp_ids:
        matches = glob.glob(os.path.join(SCANNED_DATASET_PATH, "imslp_pdfs", f"IMSLP{id}*.pdf"))
        if len(matches) == 0:
            print(f"MISSING IMSLP PDF: #{id}")
            continue
        if len(matches) > 1:
            print(f"TOO MANY IMSLP PDFs:")
            for match in matches:
                print(match)
            continue
        pdf_file = matches[0]

        # where the PNGs will be dumped
        pngs_folder = os.path.join(SCANNED_DATASET_PATH, "imslp_pngs", "IMSLP" + id)
        pngs_base_path = os.path.join(pngs_folder, "IMSLP" + id)

        # if the folder exists, just skip it
        if os.path.isdir(pngs_folder):
            # print("Skipping", id, "...")
            continue

        print("Processing IMSLP PDF", id, "...")
        
        # clear and prepare the folder
        assert os.system(f"rm -rf {pngs_folder}") == 0
        assert os.system(f"mkdir -p {pngs_folder}") == 0
        
        # extract images using pdfimages from poppler utils on ubuntu:
        # https://manpages.ubuntu.com/manpages/trusty/man1/pdfimages.1.html
        exit_code = os.system(
            f"pdfimages -png -p \"{pdf_file}\" {pngs_base_path}"
        )

        if exit_code != 0:
            assert os.system(f"rm -rf {pngs_folder}") == 0
            raise Exception("pdfimages returned with a non-zero exit code")
    
    print("IMSLP PNGs prepared.")

