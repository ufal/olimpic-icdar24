import os
import cv2
from typing import Tuple


def crop_system_from_png_page(
    page_png: str,
    bbox: Tuple[float, float, float, float], # x1, y1, x2, y2
    out_system_png: str,
    vertical_margin=0.5, # in the multiples of system height
    horizontal_margin=0.5, # in the multiples of system height
    alpha_to_black_on_white=False,
):
    """Crops out a system from a PNG page, given the system's bounding box.
    It also automatically adds some margin around the bbox and handles
    image edge collisions."""
    
    if alpha_to_black_on_white:
        img = cv2.imread(page_png, cv2.IMREAD_UNCHANGED)
        img = 255 - img[:, :, 3]
    else:
        img = cv2.imread(page_png, cv2.IMREAD_GRAYSCALE)

    img_height, img_width = img.shape

    x1, y1, x2, y2 = bbox
    height = y2 - y1

    # grow the bbox to cropbox
    x1 -= horizontal_margin * height
    x2 += horizontal_margin * height
    y1 -= vertical_margin * height
    y2 += vertical_margin * height

    # hit page border
    x1 = max(x1, 0)
    y1 = max(y1, 0)
    x2 = min(x2, img_width - 1)
    y2 = min(y2, img_height - 1)

    # round to pixel
    x1 = int(x1)
    y1 = int(y1)
    x2 = int(x2)
    y2 = int(y2)
    
    # crop the image
    system_img = img[y1:y2,x1:x2]

    # create the target directory if missing
    output_dir = os.path.dirname(out_system_png)
    os.makedirs(output_dir, exist_ok=True)

    # save the image
    cv2.imwrite(out_system_png, system_img)
