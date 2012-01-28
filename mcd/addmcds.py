# -*- coding: utf-8 -*-
#
# Portions of this code are derived from the copyrighted works of:
#    Damien Elmes <anki@ichi2.net>
#
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
#
# This project is hosted on GitHub: https://github.com/tarix/mcdsupport

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import QDialog, QCursor

from aqt import mw
from aqt.utils import showInfo, saveGeom, restoreGeom, askUser
import aqt.modelchooser
import aqt.tagedit

from cloze import Cloze
import dlgAddMcds

# TODO: put this in a proper pair and move to __init__.py
modes     = [ "space",          "semicolon",          "kanji" ]
modeNames = [ "Manual (Space)", "Manual (Semicolon)", "Kanji/Hanzi" ]

class AddMcds(QDialog):

    def __init__(self, mw):
        QDialog.__init__(self, mw, Qt.Window)
        self.mw = mw
        self.form = dlgAddMcds.Ui_Dialog()
        self.form.setupUi(self)
        self.setupCombos()
        self.setupTagsAndDeck()
        self.setupButtons()
        self.updateTagsAndDeck()
        restoreGeom(self, "addMcds")
        self.mw.requireReset(modal=True)
        self.show()

    def setupCombos(self):
		# add MCD modes
        self.form.cmbMode.addItems(modeNames)
		# TODO: save/load the last used mode
		# add the Model Chooser
        self.modelChooser = aqt.modelchooser.ModelChooser(self.mw, self.form.modelArea)
        
    def setupButtons(self):
        # set the configure icon
        self.form.pbtConfigure.setIcon(QtGui.QIcon(':/icons/configure.png'))
        self.form.pbtConfigure.hide()
        # connect the button signals to their functions
        QtCore.QObject.connect(self.form.pbtConfigure, QtCore.SIGNAL('clicked()'), self.configure)
        QtCore.QObject.connect(self.form.pbtAdd, QtCore.SIGNAL('clicked()'), self.addMcd)
        QtCore.QObject.connect(self.form.buttonBox, QtCore.SIGNAL('helpRequested()'), self.helpRequested)

    # Tag & deck handling
    ######################################################################

    def setupTagsAndDeck(self):
        # hide and remove the elements from the layout
        self.form.lneDeck.hide()
        self.form.layTags.removeWidget(self.form.lneDeck)
        self.form.lneTags.hide()
        self.form.layTags.removeWidget(self.form.lneTags)
        # create our size policy
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
		# set the deck
        self.deck = aqt.tagedit.TagEdit(self, type=1)
        self.deck.setSizePolicy(sizePolicy)
        self.form.layTags.insertWidget(1, self.deck) # put it just past the label
        # set the tags
        self.tags = aqt.tagedit.TagEdit(self)
        self.tags.setSizePolicy(sizePolicy)
        self.form.layTags.insertWidget(3, self.tags) # put it just past the label

    def updateTagsAndDeck(self):
        if self.tags.col != self.mw.col:
            if self.deck:
                self.deck.setCol(self.mw.col)
            self.tags.setCol(self.mw.col)

    # Button Events
    ######################################################################

    def configure(self):
        return showInfo("not yet implemented")

    def addMcd(self):
        # begin busy cursor
        mw.app.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.form.lblStatus.setText(u'')
        self.form.pbtAdd.setEnabled(False)
        mw.app.processEvents()
        # get all user input
        cloze = Cloze();
        cloze.mode = self.form.cmbMode.currentIndex()
        cloze.text = self.form.pteText.toPlainText()
        cloze.notes = self.form.pteNotes.toPlainText()
        cloze.source = self.form.lneSource.text()
        cloze.clozes = self.form.lneClozes.text()
        cloze.deck = self.deck.text()
        cloze.tags = self.tags.text()
		# create the note
        status = cloze.createNote()
        # update the results
        self.form.lblStatus.setText(status)
        # clear the form
        self.form.pteText.clear()
        self.form.pteNotes.clear()
        self.form.lneClozes.clear()
		# end busy cursor
        self.form.pbtAdd.setEnabled(True)
        mw.app.restoreOverrideCursor()
        
    def helpRequested(self):
        return showInfo("not yet implemented")
#        # show help text
#        ui.utils.showText(helpAddMcd, None, type='html')	

    # Dialog Close
    ######################################################################

    def reject(self):
        if not self.canClose():
            return
        self.modelChooser.cleanup()
        self.mw.maybeReset()
        saveGeom(self, "addMcds")
        QDialog.reject(self)

    def canClose(self):
        has_data = self.form.pteText.toPlainText() or self.form.pteNotes.toPlainText()
        if (not has_data or askUser(_("Close and lose current input?"))):
            return True
        return False
