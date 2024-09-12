from PySide6 import QtUiTools, QtCore


class UiLoader(QtUiTools.QUiLoader):
    _base_widget = None

    def __init__(self, base_widget=None):
        super().__init__(base_widget)
        self._base_widget = base_widget

    def createWidget(self, classname, parent=None, name=''):
        if parent is None and self._base_widget is not None:
            widget = self._base_widget
        else:
            widget = super().createWidget(classname, parent, name)
            if self._base_widget is not None:
                setattr(self._base_widget, name, widget)
        return widget

    def load_ui(self, ui_file, base_widget=None):
        self._base_widget = base_widget
        widget = self.load(ui_file)
        QtCore.QMetaObject.connectSlotsByName(base_widget)
        return widget
