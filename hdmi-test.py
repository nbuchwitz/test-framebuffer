#!/usr/bin/env/python3

import io
import logging
import shutil
import subprocess
import tempfile
from collections import Counter
from typing import Optional

from PIL import Image

## configuration for uvccapture
CAPTURE_QUALITY = 50
CAPTURE_WIDTH = 1920
CAPTURE_HEIGHT = 1080

logger = logging.getLogger()


def get_primary_color(
    image: Image, *, threshold_primary_color: int, threshold_other_colors: int
) -> Optional[str]:

    # Convert the image to RGB mode
    img_rgb = image.convert("RGB")

    # Get the pixel data
    pixels = list(img_rgb.getdata())

    # Count the occurrence of each color in the image
    color_counts = Counter(pixels)

    # Get the most common color (primary color)
    red, green, blue = color_counts.most_common(1)[0][0]

    color = None
    if (
        red > threshold_primary_color
        and green < threshold_other_colors
        and blue < threshold_other_colors
    ):
        color = "red"
    elif (
        red < threshold_other_colors
        and green > threshold_primary_color
        and blue < threshold_other_colors
    ):
        color = "green"
    elif (
        red < threshold_other_colors
        and green < threshold_other_colors
        and blue > threshold_primary_color
    ):
        color = "blue"

    return color


def capture_hdmi(device: str, *, show: bool = False) -> Image:
    with tempfile.NamedTemporaryFile() as tmpfile:
        # Run the uvccapture command to grab the HDMI input
        subprocess.check_call(
            [
                "uvccapture",
                "-m",
                "-d" + device,
                "-w",
                f"-x{CAPTURE_WIDTH}",
                f"-y{CAPTURE_HEIGHT}",
                f"-q{CAPTURE_QUALITY}",
                "-o" + tmpfile.name,
            ],
            stderr=subprocess.DEVNULL,
        )

        tmpfile.seek(0)

        image = Image.open(io.BytesIO(tmpfile.read()))

        if show:
            image.show()

    return image


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--color", type=str, choices=["red", "green", "blue"], required=True
    )
    parser.add_argument("--device", type=str, required=True)
    parser.add_argument("--threshold-primary-color", type=int, default=230)
    parser.add_argument("--threshold-other-colors", type=int, default=50)

    args = parser.parse_args()

    # check for dependency: uvccapture
    if shutil.which("uvccapture") is None:
        print(
            "ERROR: Missing program 'uvccapture'. Check if it is installed (eg. sudo apt-get install -y uvccapture)"
        )
        exit(10)

    try:
        # capture image from hdmi input
        image = capture_hdmi(args.device)

        # get primary color from captured image
        primary_color = get_primary_color(
            image,
            threshold_primary_color=args.threshold_primary_color,
            threshold_other_colors=args.threshold_other_colors,
        )
    except subprocess.CalledProcessError as cpe:
        print(f"ERROR: Failed to capture hdmi input ({cpe.returncode})")
        exit(2)

    if args.color != primary_color:
        print(f"ERROR: Image is mostly {primary_color} and not {args.color}")
        exit(1)
    else:
        print("OK: Image is mostly " + args.color)
        exit(0)
