from textual.containers import HorizontalGroup
from textual.widgets import ProgressBar, Label
from textual.timer import Timer



class StatusBar(HorizontalGroup):
    progress_timer : Timer

    def __init__(self, valueInt, labelStr, totalInt = 100, id=None):
        self.start_value = valueInt
        self.labelStr = labelStr
        self.totalInt = totalInt
        super().__init__(id=id)

    def compose(self):
        yield ProgressBar(total = self.totalInt, show_eta=False)
        yield Label(" " + self.labelStr)

    def on_mount(self) -> None:
        self.initialize_timer = self.set_interval(1 / 100, self.initialize_value, pause=False)
        self.query_one(ProgressBar).update(total=self.totalInt)

    def initialize_value(self) -> None:
        if self.query_one(ProgressBar).progress < self.start_value:
            self.query_one(ProgressBar).advance(1)
        else :
            self.initialize_timer.stop()

    def update_value(self, newValueInt) -> None:
        self.target_value = newValueInt
        self.newValueTimer = self.set_interval(1 / 100, self.smooth_value_update, pause=False)

    def smooth_value_update(self) -> None:
        if self.query_one(ProgressBar).progress < self.target_value:
            self.query_one(ProgressBar).advance(1)
        elif self.query_one(ProgressBar).progress > self.target_value:
            self.query_one(ProgressBar).advance(-1)
        else:
            self.newValueTimer.stop()