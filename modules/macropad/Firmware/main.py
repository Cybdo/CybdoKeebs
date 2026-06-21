import time

import board
import digitalio
from adafruit_hid.keycode import Keycode


from i2ctarget import I2CTarget



I2C_ADDRESS = 0x42
REPORT_LENGTH = 8
DEBOUNCE_SECONDS = 0.02
INTERRUPT_PULSE_SECONDS = 0.03

matrix = [
    ["a", "b", "c", "d"],
    ["e", "f", "g", "h"],
    ["i", "j", "k", "l"],
    ["m", "n", "o", "p"],
    ["q", "r", "s", "t"],
]

interrupt = digitalio.DigitalInOut(board.GP22)
interrupt.direction = digitalio.Direction.OUTPUT
interrupt.value = False

column_pins = [
    digitalio.DigitalInOut(board.GP18),
    digitalio.DigitalInOut(board.GP17),
    digitalio.DigitalInOut(board.GP14),
    digitalio.DigitalInOut(board.GP11),
]

row_pins = [
    digitalio.DigitalInOut(board.GP1),
    digitalio.DigitalInOut(board.GP12),
    digitalio.DigitalInOut(board.GP10),
    digitalio.DigitalInOut(board.GP2),
    digitalio.DigitalInOut(board.GP16),
]

for column_pin in column_pins:
    column_pin.direction = digitalio.Direction.OUTPUT
    column_pin.value = True

for row_pin in row_pins:
    row_pin.direction = digitalio.Direction.INPUT
    row_pin.pull = digitalio.Pull.UP


KEYCODES = {
    "a": Keycode.A,
    "b": Keycode.B,
    "c": Keycode.C,
    "d": Keycode.D,
    "e": Keycode.E,
    "f": Keycode.F,
    "g": Keycode.G,
    "h": Keycode.H,
    "i": Keycode.I,
    "j": Keycode.J,
    "k": Keycode.K,
    "l": Keycode.L,
    "m": Keycode.M,
    "n": Keycode.N,
    "o": Keycode.O,
    "p": Keycode.P,
    "q": Keycode.Q,
    "r": Keycode.R,
    "s": Keycode.S,
    "t": Keycode.T,
}


def _set_interrupt(active):
    interrupt.value = active


def _scan_matrix():
    keys = []
    seen_keys = set()

    for column_index, column_pin in enumerate(column_pins):
        column_pin.value = False
        for row_index, row_pin in enumerate(row_pins):
            if not row_pin.value:
                key_name = matrix[row_index][column_index]
                if key_name is None:
                    continue

                keycode = KEYCODES.get(key_name)
                if keycode is not None and keycode not in seen_keys:
                    seen_keys.add(keycode)
                    keys.append(keycode)
        column_pin.value = True

    report = bytearray(REPORT_LENGTH)
    report[0] = 0
    report[1] = 0
    for index, keycode in enumerate(keys[:6], start=2):
        report[index] = keycode
    return bytes(report)


def _serve_i2c(target, report):
    request = target.request()
    if request is None:
        return

    with request as transaction:
        if transaction.is_read:
            transaction.write(report)
        elif transaction.is_write:
            transaction.readinto(bytearray(REPORT_LENGTH))


def main():

    stable_report = _scan_matrix()
    candidate_report = stable_report
    candidate_since = time.monotonic()
    interrupt_clear_at = 0.0

    with I2CTarget(board.GP29, board.GP28, (I2C_ADDRESS,)) as target:
        while True:
            now = time.monotonic()
            current_report = _scan_matrix()

            if current_report != candidate_report:
                candidate_report = current_report
                candidate_since = now
            elif current_report != stable_report and now - candidate_since >= DEBOUNCE_SECONDS:
                stable_report = current_report
                _set_interrupt(True)
                interrupt_clear_at = now + INTERRUPT_PULSE_SECONDS

            if interrupt_clear_at and now >= interrupt_clear_at:
                _set_interrupt(False)
                interrupt_clear_at = 0.0

            _serve_i2c(target, stable_report)

            time.sleep(0.001)


main()

