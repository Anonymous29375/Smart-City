from machine import Pin

class Input:
    def __init__(self, pin_number: int, on_value: int, mode: int | None) -> None:
        self.on_value = on_value
        self.pin = Pin(pin_number, Pin.IN, mode)

    def value(self) -> bool:
        return self.pin.value() == self.on_value