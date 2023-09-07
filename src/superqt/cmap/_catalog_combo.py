from __future__ import annotations

from typing import TYPE_CHECKING, Container

from cmap import Colormap
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QComboBox, QCompleter, QWidget

from ._cmap_item_delegate import ColormapItemDelegate
from ._cmap_line_edit import ColormapLineEdit
from ._cmap_utils import try_cast_colormap

if TYPE_CHECKING:
    from cmap._catalog import Category, Interpolation


class CmapCatalogComboBox(QComboBox):
    """A combo box for selecting a colormap from the entire cmap catalog.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget.
    prefer_short_names : bool, optional
        If True (default), short names (without the namespace prefix) will be
        preferred over fully qualified names. In cases where the same short name is
        used in multiple namespaces, they will *all* be referred to by their fully
        qualified (namespaced) name.
    categories : Container[Category], optional
        If provided, only return names from the given categories.
    interpolation : Interpolation, optional
        If provided, only return names that have the given interpolation method.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        categories: Container[Category] = (),
        prefer_short_names: bool = True,
        interpolation: Interpolation | None = None,
    ) -> None:
        super().__init__(parent)

        # get valid names according to preferences
        word_list = sorted(
            Colormap.catalog().unique_keys(
                prefer_short_names=prefer_short_names,
                categories=categories,
                interpolation=interpolation,
            )
        )

        # initialize the combobox
        self.addItems(word_list)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.setEditable(True)
        self.setDuplicatesEnabled(False)
        # (must come before setCompleter)
        self.setLineEdit(ColormapLineEdit(self))

        # setup the completer
        completer = QCompleter(word_list)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setModel(self.model())
        self.setCompleter(completer)

        # set the delegate for both the popup and the combobox
        delegate = ColormapItemDelegate()
        completer.popup().setItemDelegate(delegate)
        self.setItemDelegate(delegate)

    def currentColormap(self) -> Colormap | None:
        """Returns the currently selected Colormap or None if not yet selected."""
        return try_cast_colormap(self.currentText())
