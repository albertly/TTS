# Author: Calumks <calumks@gmail.com>
# Get reviewer class
from aqt.reviewer import Reviewer
from aqt import  utils

# Replace _answerButtonList method
def answerButtonList(self):
    l = ((1, _("<font color='red'><b>Again</b></font>")),)
    cnt = self.mw.col.sched.answerButtons(self.card)
    if cnt == 2:
        return l + ((2, _("<font color='green'><b>Good</b></font>")),)
    elif cnt == 3:
        return l + ((2, _("<font color='green'><b>Good</b></font>")), (3, _("<b>Easy</b>")))
    else:
        return l + ((2, _("<b>Hard</b>")), (3, _("<font color='green'<b>Good</b></font>")), (4, _("<b>Easy</b>")))

Reviewer._answerButtonList = answerButtonList

def newInitWeb(self):
    self._bottomCSS = self._bottomCSS.replace("60px;", "120px; min-height:25px;")
    oldInitWeb(self)

oldInitWeb = Reviewer._initWeb
Reviewer._initWeb = newInitWeb
