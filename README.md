# CybdoKeebs!

A hotswappable ecosystem of i2c powered keyboard modules!

<img width="401" height="614" alt="Zine" src="https://github.com/user-attachments/assets/36e9397b-e3a6-466a-815b-8bfe1fb51e0a" />


I made this project because I wanted to make something cooler than a macropad, and being able to just swap stuff around seemed really sick.=

Inspired by [Ocreeb](https://www.youtube.com/watch?v=7DfexfHzT-w)!

# File structure

everything for each module is found under `modules/[module name]`, including CAD files, EDA files and firmware.

# Features
 - plug and play
 - hotswappable modules
 - exposed I2C buses
 - fully open source!
 - supports any MX-footprint keyswitches!
 - inbuilt USB hub in the controller

# Firmware
Firmware runs on circuitpython, and the firmware for each module is under `modules/[module name]/firmware`. Flash it using the SWD ports on each module, or via USB on the controller hub. You may need a SWD to USB converter, which can be made using a Raspberry Pi Pico.

# Custom modules
Each module is made as a composite of "sub units", each being 6cm tall and 5cm wide, with male pogo pins on the top and left sides, and female recievers on the bottom and right sides. These can be found here: https://www.aliexpress.com/item/1005005284441979.html

# BOM
found at `bom.csv`, assuming 1 controller hub, one keyboard and one macropad

# Schematics

## Hub
<img width="1005" height="721" alt="image" src="https://github.com/user-attachments/assets/364769d2-0111-4453-b89c-a51ba62ed32a" />

## Macropad
<img width="1090" height="776" alt="image" src="https://github.com/user-attachments/assets/ef047c56-c687-4eb4-9604-1097e7c3d57c" />
<img width="483" height="624" alt="image" src="https://github.com/user-attachments/assets/0e166dfe-3d54-45f9-a60b-01ff5c13addf" />

## Keyboard
<img width="894" height="779" alt="image" src="https://github.com/user-attachments/assets/fd94f644-8be0-4a89-87f3-2a0c119c335e" />
<img width="1061" height="741" alt="image" src="https://github.com/user-attachments/assets/1eed5743-d8b8-41d8-8116-9885d837f108" />


# PCB

## Hub
<img width="1105" height="143" alt="image" src="https://github.com/user-attachments/assets/723b3de5-fae6-495b-8fa9-b3af30193b9e" />

## Macropad
<img width="719" height="834" alt="image" src="https://github.com/user-attachments/assets/0078520c-c13f-4f9f-ac00-9aa92dab00e4" />


## Keyboard

<img width="1102" height="443" alt="image" src="https://github.com/user-attachments/assets/29a2cda8-c334-4d93-bbe5-17e4d4c4d65f" />



# Acknowledgements
 - [KiCad](https://www.kicad.org)
 - [Hack Club Fallout](https://fallout.hackclub.com)
 - [Ocreeb V2](https://github.com/sb-ocr/ocreeb-mk-2)
 - [CircuitPython](https://circuitpython.org/)
