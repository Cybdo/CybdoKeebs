# CybdoKeebs
CybdoKeebs is a (WIP) ecosystem of hotswappable modules for the ultimate modular keyboard setup.

## Technical details
Each module communicates to the host via one of 6 I2C buses. Each module can contain any peripherals, as long as it is implemented in the firmware and can communicate over I2C.
The central controller hub contains a RP2354 to decode I2C and turn it into USB HID signals, and also a USB hub for acessories such as a mouse dongle.

## Folder structure

```
Root
  modules
    template
      PCB
        contains kicad files for the pcb
      Firmware
        contains micropython firmware code
      CAD
        contains 3D cad files, including rendering files, cases, etc.
      README.md
        description of each module
    ...
  assets
    renders
      contains render images
    schematics
      contains schematics of each module in pdf form
    silkscreen
      contains raw files for silkscreen art


```
