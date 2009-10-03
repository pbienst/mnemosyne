#
# activate_cards_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.ui_activate_cards_dlg import Ui_ActivateCardsDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ActivateCardsDialog
from mnemosyne.libmnemosyne.activity_criteria.default_criterion import \
     DefaultCriterion


class ActivateCardsDlg(QtGui.QDialog, Ui_ActivateCardsDlg,
                       ActivateCardsDialog):

    """Note that this dialog can support active tags and forbidden tags,
    but not at the same time, in order to keep the interface compact.

    """

    def __init__(self, component_manager):
        ActivateCardsDialog.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        # Restore sizes.
        config = self.config()
        width, height = config["activate_cards_dlg_size"]
        if width:
            self.resize(width, height)
        splitter_sizes = config["activate_cards_dlg_splitter"]
        if not splitter_sizes:
            self.splitter.setSizes([100, 350])
        else:
            self.splitter.setSizes(splitter_sizes)
        # Fill card types tree widget.
        criterion = self.database().current_activity_criterion()
        self.card_type_fact_view_ids_for_node_item = {}
        root_item = QtGui.QTreeWidgetItem(self.card_types_tree,
            [_("All card types")], 0)
        root_item.setFlags(root_item.flags() | \
           QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate)
        root_item.setCheckState(0, QtCore.Qt.Checked)
        for card_type in self.card_types():
            card_type_item = QtGui.QTreeWidgetItem(root_item,
                [card_type.name], 0)
            card_type_item.setFlags(card_type_item.flags() | \
                QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate)            
            card_type_item.setCheckState(0, QtCore.Qt.Checked)
            for fact_view in card_type.fact_views:
                fact_view_item = QtGui.QTreeWidgetItem(card_type_item,
                                                       [fact_view.name], 0)
                fact_view_item.setFlags(fact_view_item.flags() | \
                    QtCore.Qt.ItemIsUserCheckable)
                if (card_type.id, fact_view.id) in \
                    criterion.deactivated_card_type_fact_view_ids:
                    check_state = QtCore.Qt.Unchecked
                else:
                    check_state = QtCore.Qt.Checked
                fact_view_item.setCheckState(0, check_state)
                self.card_type_fact_view_ids_for_node_item[fact_view_item] = \
                    (card_type.id, fact_view.id)
        self.card_types_tree.expandAll()
        # Fill tags tree widget.
        self.tag_for_node_item = {}
        root_item = QtGui.QTreeWidgetItem(self.tags_tree, [_("All tags")], 0)
        root_item.setFlags(root_item.flags() | \
           QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate)
        root_item.setCheckState(0, QtCore.Qt.Checked)
        self.tag_for_node_item = {}
        node_item_for_partial_tag = {}
        for tag in self.database().get_tags():
            parent = root_item
            partial_tag = ""
            node_item = None
            for node in tag.name.split("::"):
                node += "::"
                partial_tag += node
                if partial_tag not in node_item_for_partial_tag:
                    node_item = QtGui.QTreeWidgetItem(parent, [node[:-2]], 0)
                    node_item.setFlags(node_item.flags() | \
                        QtCore.Qt.ItemIsUserCheckable | \
                        QtCore.Qt.ItemIsTristate)
                    node_item_for_partial_tag[partial_tag] = node_item
                parent = node_item_for_partial_tag[partial_tag]
            self.tag_for_node_item[node_item] = tag
        # Set forbidden tags.
        if len(criterion.forbidden_tag__ids):
            self.active_or_forbidden.setCurrentIndex(1)
            for node_item, tag in self.tag_for_node_item.iteritems():
                if tag._id in criterion.forbidden_tag__ids:
                    node_item.setCheckState(0, QtCore.Qt.Checked)
                else:
                    node_item.setCheckState(0, QtCore.Qt.Unchecked)  
        # Set active tags.
        elif len(criterion.active_tag__ids):
            self.active_or_forbidden.setCurrentIndex(0)
            for node_item, tag in self.tag_for_node_item.iteritems():
                if tag._id in criterion.active_tag__ids:
                    node_item.setCheckState(0, QtCore.Qt.Checked)
                else:
                    node_item.setCheckState(0, QtCore.Qt.Unchecked)
        # Finalise.
        self.tags_tree.sortItems(0, QtCore.Qt.AscendingOrder)
        self.tags_tree.expandAll()
                    
    def activate(self):
        self.exec_()

    def _store_layout(self):
        self.config()["activate_cards_dlg_size"] = \
            (self.width(), self.height())
        self.config()["activate_cards_dlg_splitter"] = \
            self.splitter.sizes()
        
    def closeEvent(self, event):
        self._store_layout()
        
    def _criterion(self):
        criterion = DefaultCriterion(self.component_manager)
        # Card types and fact views.
        for item, card_type_fact_view_ids in \
                self.card_type_fact_view_ids_for_node_item.iteritems():
            if item.checkState(0) == QtCore.Qt.Unchecked:
                criterion.deactivated_card_type_fact_view_ids.add(\
                    card_type_fact_view_ids)
        # Tag tree contains active tags.
        if self.active_or_forbidden.currentIndex() == 0: 
            for item, tag in self.tag_for_node_item.iteritems():
                if item.checkState(0) == QtCore.Qt.Checked:
                    criterion.active_tag__ids.add(tag._id)
            criterion.forbidden_tags = set()
        # Tag tree contains forbidden tags.
        else:
            for item, tag in self.tag_for_node_item.iteritems():
                if item.checkState(0) == QtCore.Qt.Checked:
                    criterion.forbidden_tag__ids.add(tag._id)
            criterion.active_tags = set(self.tag_for_node_item.values())
        return criterion
            
    def accept(self):
        self.database().set_current_activity_criterion(self._criterion())
        self._store_layout()
        return QtGui.QDialog.accept(self)

    def save(self):
        from mnemosyne.pyqt_ui.card_set_name_dlg import CardSetNameDlg
        return CardSetNameDlg(\
            self.component_manager, self._criterion()).exec_()

    def reject(self):
        self._store_layout()
        QtGui.QDialog.reject(self)