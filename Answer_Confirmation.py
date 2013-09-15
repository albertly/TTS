# -*- coding: utf-8 -*-
# Author:  Albert Lyubarsky
# Email: albert.lyubarsky@gmail.com
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
#   Answer Confirmation plugin for Anki 2.0
__version__ = "1.1.0"


from aqt.reviewer import Reviewer
from aqt.utils import tooltip
from anki.hooks import wrap


def answerCard_before(self, ease) :
	checked = False

	if ease == 1  :
		tags = self.mw.reviewer.card.note().stringTags()
		if self.card.template()['name'] == "Translation" :
			if tags.find('pt') != -1 :
				checked = True
			else :
				checked = False
		elif self.card.template()['name'] == "Forward" :
			if tags.find('pf') != -1 :
				checked = True
			else :
				checked = False
		elif self.card.template()['name'] == "Reverse" :
			if tags.find('pb') != -1 :
				checked = True
			else :
				checked = False
				
	if checked :
		self.state = None
		tooltip("Defered Card!")
	else :
		l = self._answerButtonList()
		a = [item for item in l if item[0] == ease]
		if len(a) > 0 :
			tooltip(a[0][1])
		
def answerCard_after(self, ease) :
	if self.state == None :
		self.state = "answer"


Reviewer._answerCard  = wrap(Reviewer._answerCard, answerCard_before, "before")
Reviewer._answerCard  = wrap(Reviewer._answerCard, answerCard_after, "after")
