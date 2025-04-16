from textual.containers import VerticalGroup, HorizontalGroup
from ..SelectionMenu.SelectionMenu import SelectionMenu
from ..TableList.TableList import TableList
from ..StatusBar.StatusBar import StatusBar


class ViewPort(VerticalGroup):

    def __init__(self, id=None):
        super().__init__(id=id)

    def compose(self):
        yield HorizontalGroup()

    def present_options(self, id=None, option_values=None, title=None):
        this_viewport = self
        this_viewport.remove_children()
        new_selection = SelectionMenu(option_values=option_values, title=title)
        this_viewport.mount(new_selection)

    def present_table(self, id=None, headers=None, data=None, title=None):
        this_viewport = self
        this_viewport.remove_children()
        new_table = TableList(headers=headers, data=data, title=title)
        this_viewport.mount(new_table)

    def present_loadbar(self, id=None, label=None, animation_interval=100):
        this_viewport = self
        this_viewport.remove_children()
        new_statusbar = StatusBar(valueInt=100, labelStr=label, totalInt=100, animation_interval=animation_interval)
        this_viewport.mount(new_statusbar)