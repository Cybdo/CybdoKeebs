import time

import board
import digitalio
from adafruit_hid.keycode import Keycode

try:
    from i2ctarget import I2CTarget
except ImportError:
    I2CTarget = None


I2C_ADDRESS = 0x42
REPORT_LENGTH = 8
DEBOUNCE_SECONDS = 0.02
INTERRUPT_PULSE_SECONDS = 0.03

matrix = [
    ["esc", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "backspace"],
    ["tab", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]", "\\"],
    ["capslock", "a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'", None, "enter"],
    ["Lshift", "z", "x", "c", "v", "b", "n", "m", ",", ".", "/", None, None, "Rshift"],
    ["Lctrl", "Lwin", "Lalt", None, None, "Space", None, None, None, None, None, "Ralt", "Rwin", "Rctrl"],
]

interrupt = digitalio.DigitalInOut(board.GP29)
interrupt.direction = digitalio.Direction.OUTPUT
interrupt.value = False

column_pins = [
    digitalio.DigitalInOut(board.GP0),
    digitalio.DigitalInOut(board.GP1),
    digitalio.DigitalInOut(board.GP2),
    digitalio.DigitalInOut(board.GP3),
    digitalio.DigitalInOut(board.GP10),
    digitalio.DigitalInOut(board.GP14),
    digitalio.DigitalInOut(board.GP15),
    digitalio.DigitalInOut(board.GP16),
    digitalio.DigitalInOut(board.GP17),
    digitalio.DigitalInOut(board.GP19),
    digitalio.DigitalInOut(board.GP20),
    digitalio.DigitalInOut(board.GP21),
    digitalio.DigitalInOut(board.GP18),
    digitalio.DigitalInOut(board.GP22),
]

row_pins = [
    digitalio.DigitalInOut(board.GP13),
    digitalio.DigitalInOut(board.GP12),
    digitalio.DigitalInOut(board.GP11),
    digitalio.DigitalInOut(board.GP9),
    digitalio.DigitalInOut(board.GP8),
]

for column_pin in column_pins:
    column_pin.direction = digitalio.Direction.OUTPUT
    column_pin.value = True

for row_pin in row_pins:
    row_pin.direction = digitalio.Direction.INPUT
    row_pin.pull = digitalio.Pull.UP


KEYCODES = {
    "esc": Keycode.ESCAPE,
    "1": Keycode.ONE,
    "2": Keycode.TWO,
    "3": Keycode.THREE,
    "4": Keycode.FOUR,
    "5": Keycode.FIVE,
    "6": Keycode.SIX,
    "7": Keycode.SEVEN,
    "8": Keycode.EIGHT,
    "9": Keycode.NINE,
    "0": Keycode.ZERO,
    "-": Keycode.MINUS,
    "=": Keycode.EQUALS,
    "backspace": Keycode.BACKSPACE,
    "tab": Keycode.TAB,
    "q": Keycode.Q,
    "w": Keycode.W,
    "e": Keycode.E,
    "r": Keycode.R,
    "t": Keycode.T,
    "y": Keycode.Y,
    "u": Keycode.U,
    "i": Keycode.I,
    "o": Keycode.O,
    "p": Keycode.P,
    "[": Keycode.LEFT_BRACKET,
    "]": Keycode.RIGHT_BRACKET,
    "\\": Keycode.BACKSLASH,
    "capslock": Keycode.CAPS_LOCK,
    "a": Keycode.A,
    "s": Keycode.S,
    "d": Keycode.D,
    "f": Keycode.F,
    "g": Keycode.G,
    "h": Keycode.H,
    "j": Keycode.J,
    "k": Keycode.K,
    "l": Keycode.L,
    ";": Keycode.SEMICOLON,
    "'": Keycode.QUOTE,
    "enter": Keycode.ENTER,
    "z": Keycode.Z,
    "x": Keycode.X,
    "c": Keycode.C,
    "v": Keycode.V,
    "b": Keycode.B,
    "n": Keycode.N,
    "m": Keycode.M,
    ",": Keycode.COMMA,
    ".": Keycode.PERIOD,
    "/": Keycode.FORWARD_SLASH,
    "Space": Keycode.SPACEBAR,
}

MODIFIER_BITS = {
    "Lctrl": 0x01,
    "Lshift": 0x02,
    "Lalt": 0x04,
    "Lwin": 0x08,
    "Rctrl": 0x10,
    "Rshift": 0x20,
    "Ralt": 0x40,
    "Rwin": 0x80,
}


def _set_interrupt(active):
    interrupt.value = active


def _scan_matrix():
    modifiers = 0
    keys = []
    seen_keys = set()

    for column_index, column_pin in enumerate(column_pins):
        column_pin.value = False
        for row_index, row_pin in enumerate(row_pins):
            if not row_pin.value:
                key_name = matrix[row_index][column_index]
                if key_name is None:
                    continue

                modifier_bit = MODIFIER_BITS.get(key_name)
                if modifier_bit is not None:
                    modifiers |= modifier_bit
                    continue

                keycode = KEYCODES.get(key_name)
                if keycode is not None and keycode not in seen_keys:
                    seen_keys.add(keycode)
                    keys.append(keycode)
        column_pin.value = True

    report = bytearray(REPORT_LENGTH)
    report[0] = modifiers
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
    if I2CTarget is None:
        raise RuntimeError("i2ctarget is required for the keyboard peripheral firmware")

    stable_report = _scan_matrix()
    candidate_report = stable_report
    candidate_since = time.monotonic()
    interrupt_clear_at = 0.0

    with I2CTarget(board.GP25, board.GP24, (I2C_ADDRESS,)) as target:
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

