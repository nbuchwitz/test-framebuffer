# Framebuffer Test

This repository provides a tool `fb-control.py` to fill the complete area of a given framebuffer with a solid color. If the framebuffer is attached to a video output (eg. HDMI or others) it can be then captured with `hdmi-test.py` and checked if the colors match.

## Install Dependencies on test PC

```
sudo apt install uvccapture python3-pil
```

## Usage

### DUT

Set color on DUT:

```
python3 fb-control.py --mode color --color red
```

```
python3 fb-control.py --mode color --color green
```

```
python3 fb-control.py --mode color --color blue
```

> **NOTE:** The terminal can be reset with the following command: `python3 fb-control.py --mode tty`


### Test PC

Capture screen input on test PC and test for primary color (change `/dev/video0` as needed):

```
python3 hdmi-test.py --device /dev/video0 --color red
```

```
python3 hdmi-test.py --device /dev/video0 --color green
```

```
python3 hdmi-test.py --device /dev/video0 --color blue
```
