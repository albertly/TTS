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
from Dictionaries import DictionaryParser,Google
from GoogleTTS import GetExamples
import traceback
import warnings

def bulkCopy(nids):

    mw.progress.start(immediate=True)

    for nid in nids:
        note = mw.col.getNote(nid)
        word = note[srcField]
        try :    
                with warnings.catch_warnings():
                    warnings.simplefilter("error")
                    mw.progress.update(label=word)
                    GetExamples(word)
                    g = Google()
                    g.write(word)
                    dp = DictionaryParser(word)
                    dp.format()
        except :
#            mw.progress.clear()
#            utils.showInfo("Exception " + word)
            txt = "<h3>" + word + "</h3>" 
            txt += "<div style='white-space: pre-wrap'>" + traceback.format_exc() + "</div>"
            utils.showText(txt, type="html")
            pass

    mw.progress.finish()


def setupMenu(browser):
    a = QAction("Bulk-Copy Field Data", browser)
    browser.connect(a, SIGNAL("triggered()"), lambda e=browser: onBulkCopy(e))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)

def onBulkCopy(browser):
    bulkCopy(browser.selectedNotes())

addHook("browser.setupMenus", setupMenu)
