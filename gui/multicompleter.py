from PyQt5.QtWidgets import QCompleter


class MultiCompleter(QCompleter):
    """ Multi Tag completer, allows for comma separated tag searching"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setMaxVisibleItems(5)

    def pathFromIndex(self, index):
        path = super().pathFromIndex(index)

        lst = str(self.widget().text()).split(', ')
        if len(lst) > 1:
            path = ', '.join(lst[:-1]) + ', ' + path

        return path

    def splitPath(self, path):
        return [path.split(',')[-1].strip()]