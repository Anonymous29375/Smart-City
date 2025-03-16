class BankState:

    def __init__(self) -> None:
        self.in_alarm = False
        self.is_armed = False
        self.is_remote_armed = False
        self.door_open = False
        self.beam_triggered = False

    