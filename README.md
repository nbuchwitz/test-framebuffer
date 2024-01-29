# HDMI Test

## Install Dependencies on test PC

```
sudo apt install uvccapture python3-pil
```

## Usage

### DUT

Set color on DUT:

```
python3 hdmi-control.py --mode color --color red
```

```
python3 hdmi-control.py --mode color --color green
```

```
python3 hdmi-control.py --mode color --color blue
```

> **NOTE:** The terminal can be reset with the following command: `python3 hdmi-control.py --mode tty`


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