import argparse
import fcntl
import os
import struct

KDSETMODE = 0x4B3A
KD_TEXT = 0x00
KD_GRAPHICS = 0x01
FBIOGET_VSCREENINFO = 0x4600

# colors defined in BGRA (right to left) format
_colors = {"red": 0xFFFF0000, "green": 0xFF00FF00, "blue": 0xFF0000FF}


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


def fill_framebuffer_with_color(color: str, framebuffer: int = 0) -> None:
    """Fill framebuffer with one color."""
    fb = os.open(f"/dev/fb{framebuffer}", os.O_RDWR)

    # Get the screen size
    screen_info = struct.unpack(
        "HHHH", fcntl.ioctl(fb, FBIOGET_VSCREENINFO, struct.pack("HHHH", 0, 0, 0, 0))
    )
    screen_width, screen_height = screen_info[0], screen_info[2]
    screen_size = screen_width * screen_height

    color_value = _colors.get(color, None)
    if color_value is None:
        raise ValueError("Invalid color specified.")

    # Fill the framebuffer with the specified color
    data = struct.pack("I", color_value) * screen_size
    os.write(fb, data)

    os.close(fb)


if __name__ == "__main__":
    if os.geteuid() != 0:
        print("insufficient permission: script needs root permissions.")
        exit(1)

    known_colors = list(_colors.keys())

    parser = argparse.ArgumentParser()
    parser.add_argument("--color", type=str, choices=known_colors, default=known_colors[0])
    parser.add_argument("--mode", type=str, choices=["color", "tty"], required=True)
    parser.add_argument("--tty", type=str, required=False, default="/dev/tty0")

    args = parser.parse_args()

    if args.mode == "color" and args.color:
        tty_graphics_mode(args.tty)
        fill_framebuffer_with_color(args.color)
    else:
        tty_text_mode(args.tty)
