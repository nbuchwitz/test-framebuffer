#!/usr/bin/env python3
"""Show either a solid color on framebufer or reset to text mode."""

import argparse
import fcntl
import os
import stat
import struct
import sys

KDSETMODE = 0x4B3A
KD_TEXT = 0x00
KD_GRAPHICS = 0x01
FBIOGET_VSCREENINFO = 0x4600

# list of supported colors as RGB values
colors = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "orange": (255, 102, 0),
}


def tty_set_mode(tty_name: str, kd_mode: int) -> None:
    """Set text/graphics mode for tty (see ioctl_console(2))."""
    with open(tty_name, "r") as tty:
        fcntl.ioctl(tty, KDSETMODE, kd_mode)


def tty_text_mode(tty_name: str) -> None:
    """Set tty to text mode."""
    tty_set_mode(tty_name, KD_TEXT)


def tty_graphics_mode(tty_name: str) -> None:
    """Set tty to graphics mode."""
    tty_set_mode(tty_name, KD_GRAPHICS)


def is_char_device(path: str) -> bool:
    """Check if a given path is a character device."""
    try:
        st = os.stat(path)
        return stat.S_ISCHR(st.st_mode)
    except (FileNotFoundError, Exception):
        return False


def fill_framebuffer_with_color(color: str, framebuffer: int = 0) -> None:
    """Fill framebuffer with one color."""
    if color not in colors:
        raise ValueError("Invalid color specified.")

    device = f"/dev/fb{framebuffer}"
    if not is_char_device(device):
        raise ValueError(f"Framebuffer '{device}' doesn't exist or not a character device")

    red, green, blue = colors.get(color)
    # set alpha to max value as is only matters for RGBA anyway
    alpha = 255

    assert 0 <= red <= 255 and 0 <= green <= 255 and 0 <= blue <= 255

    fb = os.open(device, os.O_RDWR)
    # Get info about framebuffer (size, bpp, color channels...)
    # See fb_var_screeninfo (linux/fb.h)
    fmt = "20I"
    screen_info = struct.unpack(
        fmt, fcntl.ioctl(fb, FBIOGET_VSCREENINFO, bytes(struct.calcsize(fmt)))
    )
    screen_width, screen_height = screen_info[0], screen_info[1]
    bits_per_pixel = screen_info[6]
    offset_red, len_red = screen_info[8:10]
    offset_green, len_green = screen_info[11:13]
    offset_blue, len_blue = screen_info[14:16]
    offset_alpha, len_alpha = screen_info[17:19]

    # Calculate each channel's value according to length and offset
    red = (red >> (8 - len_red)) << offset_red
    green = (green >> (8 - len_green)) << offset_green
    blue = (blue >> (8 - len_blue)) << offset_blue
    alpha = (alpha >> (8 - len_alpha)) << offset_alpha

    color_value = red + green + blue + alpha

    if bits_per_pixel == 32:
        fmt = "I"
    elif bits_per_pixel == 16:
        fmt = "H"
    else:
        raise ValueError(f"Unsupported bits per pixel: {bits_per_pixel}")

    # Fill the framebuffer with the specified color
    data = struct.pack(fmt, color_value) * screen_width * screen_height
    os.write(fb, data)

    os.close(fb)


if __name__ == "__main__":
    if os.geteuid() != 0:
        print("insufficient permission: script needs root permissions.")
        exit(1)

    known_colors = list(colors.keys())

    parser = argparse.ArgumentParser()
    parser.add_argument("--color", type=str, choices=known_colors, help="Name of color")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["color", "tty"],
        default="color",
        help="Operation mode (defaults to color)",
    )
    parser.add_argument("--tty", type=str, required=False, default="/dev/tty0")
    parser.add_argument(
        "--fb",
        type=int,
        required=False,
        default=0,
        help="Framebuffer id (defaults to 0)",
    )

    args = parser.parse_args()

    if args.mode == "color" and not args.color:
        print("Error: --color is required when --mode is set to 'color'.", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    elif args.mode == "tty" and args.color:
        print(
            "Error: --color cannot be used when --mode is set to 'tty'.",
            file=sys.stderr,
        )
        parser.print_help()
        sys.exit(1)

    try:
        if args.mode == "color" and args.color:
            tty_graphics_mode(args.tty)
            fill_framebuffer_with_color(args.color, args.fb)
        else:
            tty_text_mode(args.tty)
    except Exception as e:
        print("Error:", str(e), file=sys.stderr)
        exit(1)
