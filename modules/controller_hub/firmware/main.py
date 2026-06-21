import time

import board
import busio
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode


I2C_ADDRESS = 0x42
REPORT_LENGTH = 8

MODIFIER_KEYCODES = [
	Keycode.LEFT_CONTROL,
	Keycode.LEFT_SHIFT,
	Keycode.LEFT_ALT,
	Keycode.LEFT_GUI,
	Keycode.RIGHT_CONTROL,
	Keycode.RIGHT_SHIFT,
	Keycode.RIGHT_ALT,
	Keycode.RIGHT_GUI,
]

bus1interrupt = digitalio.DigitalInOut(board.GP3)
bus1interrupt.direction = digitalio.Direction.INPUT
bus1interrupt.pull = digitalio.Pull.DOWN
bus1i2c = busio.I2C(board.GP5, board.GP4, frequency=100000)

bus2interrupt = digitalio.DigitalInOut(board.GP7)
bus2interrupt.direction = digitalio.Direction.INPUT
bus2interrupt.pull = digitalio.Pull.DOWN
bus2i2c = busio.I2C(board.GP9, board.GP8, frequency=100000)

bus3interrupt = digitalio.DigitalInOut(board.GP11)
bus3interrupt.direction = digitalio.Direction.INPUT
bus3interrupt.pull = digitalio.Pull.DOWN
bus3i2c = busio.I2C(board.GP13, board.GP12, frequency=100000)

bus4interrupt = digitalio.DigitalInOut(board.GP16)
bus4interrupt.direction = digitalio.Direction.INPUT
bus4interrupt.pull = digitalio.Pull.DOWN
bus4i2c = busio.I2C(board.GP18, board.GP17, frequency=100000)

bus5interrupt = digitalio.DigitalInOut(board.GP19)
bus5interrupt.direction = digitalio.Direction.INPUT
bus5interrupt.pull = digitalio.Pull.DOWN
bus5i2c = busio.I2C(board.GP21, board.GP20, frequency=100000)

bus6interrupt = digitalio.DigitalInOut(board.GP22)
bus6interrupt.direction = digitalio.Direction.INPUT
bus6interrupt.pull = digitalio.Pull.DOWN
bus6i2c = busio.I2C(board.GP24, board.GP23, frequency=100000)


keyboard = Keyboard(usb_hid.devices)

BUSES = [
	{"interrupt": bus1interrupt, "i2c": bus1i2c, "report": bytearray(REPORT_LENGTH), "last_report": bytes(REPORT_LENGTH)},
	{"interrupt": bus2interrupt, "i2c": bus2i2c, "report": bytearray(REPORT_LENGTH), "last_report": bytes(REPORT_LENGTH)},
	{"interrupt": bus3interrupt, "i2c": bus3i2c, "report": bytearray(REPORT_LENGTH), "last_report": bytes(REPORT_LENGTH)},
	{"interrupt": bus4interrupt, "i2c": bus4i2c, "report": bytearray(REPORT_LENGTH), "last_report": bytes(REPORT_LENGTH)},
	{"interrupt": bus5interrupt, "i2c": bus5i2c, "report": bytearray(REPORT_LENGTH), "last_report": bytes(REPORT_LENGTH)},
	{"interrupt": bus6interrupt, "i2c": bus6i2c, "report": bytearray(REPORT_LENGTH), "last_report": bytes(REPORT_LENGTH)},
]


def _read_report(i2c_bus, report_buffer):
    while not i2c_bus.try_lock():
        pass
    
    i2c_bus.readfrom_into(I2C_ADDRESS, report_buffer)
    i2c_bus.unlock()
    return bytes(report_buffer)




def _aggregate_state():
	modifiers = 0
	keys = []
	seen_keys = set()

	for bus in BUSES:
		report = bus["report"]
		modifiers |= report[0]

		key_count = report[1]
		if key_count > 6:
			key_count = 6

		for keycode in report[2 : 2 + key_count]:
			if keycode and keycode not in seen_keys:
				seen_keys.add(keycode)
				keys.append(keycode)
				if len(keys) == 6:
					break

	return modifiers, keys


def _sync_keyboard_state(desired_modifiers, desired_keys, current_modifiers, current_keys):
	released_modifiers = []
	pressed_modifiers = []

	for bit_index, keycode in enumerate(MODIFIER_KEYCODES):
		bit = 1 << bit_index
		if current_modifiers & bit and not desired_modifiers & bit:
			released_modifiers.append(keycode)
		elif desired_modifiers & bit and not current_modifiers & bit:
			pressed_modifiers.append(keycode)

	released_keys = [keycode for keycode in current_keys if keycode not in desired_keys]
	pressed_keys = [keycode for keycode in desired_keys if keycode not in current_keys]

	if released_modifiers or released_keys:
		keyboard.release(*(released_modifiers + released_keys))
	if pressed_modifiers or pressed_keys:
		keyboard.press(*(pressed_modifiers + pressed_keys))

	return desired_modifiers, desired_keys[:]


def main():
	current_modifiers = 0
	current_keys = []

	while True:
		updated = False

		for bus in BUSES:
			if not bus["interrupt"].value:
				continue

			report = _read_report(bus["i2c"], bus["report"])
			if report is None:
				continue

			if report != bus["last_report"]:
				bus["last_report"] = report
				updated = True

		if updated:
			for bus in BUSES:
				bus["report"][:] = bus["last_report"]

			desired_modifiers, desired_keys = _aggregate_state()
			if desired_modifiers != current_modifiers or desired_keys != current_keys:
				current_modifiers, current_keys = _sync_keyboard_state(
					desired_modifiers,
					desired_keys,
					current_modifiers,
					current_keys,
				)

		time.sleep(0.001)


main()

