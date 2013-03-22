# -*- coding: utf-8 -*-
# Copyright: Chris Langewisch <ccl09c@my.fsu.edu>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# Based on japanese.reading by Damien Elmes <anki@ichi2.net>
# Bulk copy data in one field to another.

##########################################################################


# each field name must be exact!
srcField = 'Front'

##########################################################################

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from anki.hooks import addHook
from aqt import mw, utils
from Dictionaries import DictionaryParser

def bulkCopy(nids):

    mw.progress.start()

    for nid in nids:
        note = mw.col.getNote(nid)
        try :
            dp = DictionaryParser(note[srcField])
            dp.format()
        except UnicodeDecodeError as e:
            utils.showInfo("UnicodeDecodeError " + note[srcField])



    mw.progress.finish()


def setupMenu(browser):
    a = QAction("Bulk-Copy Field Data", browser)
    browser.connect(a, SIGNAL("triggered()"), lambda e=browser: onBulkCopy(e))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)

def onBulkCopy(browser):
    bulkCopy(browser.selectedNotes())

addHook("browser.setupMenus", setupMenu)
