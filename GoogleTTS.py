# -*- coding: utf-8 -*-
# Author:  Arthur Helfstein Fragoso
# Email: arthur@life.net.br
# Based on: "hello-world plugin", "aprendiendoTTS" and "Japanese Support"
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
#   GoogleTTS plugin for Anki 2.0
version = '0.2.19 Release'
#
#   Any problems, comments, please post in this thread:  (or email me: arthur@life.net.br )
#
#   http://groups.google.com/group/ankisrs/browse_thread/thread/98177e2770659b31
#
#  Edited on 2012-08-07
#  
#
########################### Instructions #######################################
# 
# In your cards, you can add: [GTTS:language_code:text] and GoogleTTS will read it for you. 
# you may have many different languages in the same field
# note that each tag is limited to 100 characters.
# example: [GTTS:en:Hello, whats your name?] [GTTS:zh:你好吗？] [GTTS:ja:はい]
#
# so if you want GoogleTTS to read a field for you, you can edit your card's model and leave it like:
# [GTTS:en:{{Field Name}}]
#
# To hide the [GTTS::] tag and everything inside it in a card model (only) (thanks Rdamon for the idea)
# <!-- [GTTS:en:{{Field Name}}] -->
#
# to hide it while editing a card, the only way I know is:
# <span style="color:#ffffff;">[GTTS:en:Hello World]</span>
#
# The [GTTS::] tag will only read the cards on the Anki Desktop.
# If you want it to work on the mobile, you need to generate the MP3 files.
#
## Proxy - If you use a proxy connection, GoogleTTS plugin will use the configuration
# from Anki's proxy confirguration (Settings > Preferences > Network > Proxy) 
# it will only take effect after restarting Anki. If Anki's proxy configuration is
# empty, it will try to use the Operational System proxy configuration.
#
# Thanks Scott Otterson for contributing with the proxy code.
# Thanks Dusan Arsenijevic for contributing with a way to not fall in Google's blacklist while doing the Mass Generator.
#

from PyQt4.QtCore import *
TTS_read_field = {}
TTS_tags_only, TTS_if_no_tag_read_whole = [1,2]


# Key to get the [GTTS::] tags in the Question field pronounced
TTS_KEY_Q=Qt.Key_F3

# Key to get the [GTTS::] tags in the Answer field pronounced
#TTS_KEY_A=Qt.Key_F4

# Key to get the whole Question field pronounced, if there is a [GTTS::] tags, it will only read the tags
#TTS_KEY_Q_ALL=Qt.Key_F6

# Key to get the whole Answer field pronounced, if there is a [GTTS::] tags, it will only read the tags
#TTS_KEY_A_ALL=Qt.Key_F7
TTS_read_field['Front'] =  Qt.Key_F3
TTS_read_field['Back'] = Qt.Key_F4
TTS_read_field['Example'] =  Qt.Key_F5


#sorry, the TTS won't recite it automatically when there is a sound file in the Question/Answer

# Option to automatically recite the Question field as it appears:
#automaticQuestions = False 			 # disable the automatic recite
#automaticQuestions = TTS_tags_only               # recite only [GTTS::] tags in the Questions as it appears
automaticQuestions = TTS_if_no_tag_read_whole    # always recite the whole, but if there is a [GTTS::], it will only read the tags

# Option to automatically recite the Answers field as it appears
#automaticAnswers = False                         # disable the automatic recite
#automaticAnswers = TTS_tags_only                 # recite only [GTTS::] tags in the Answers as it appears
automaticAnswers = TTS_if_no_tag_read_whole      # always recite the whole, but if there is a [GTTS::], it will only read the tags


#
# Keys to get the fields pronounced, case sensitive
# uncomment and change in a way that works for you,
# you can add as many as you want
# examples:
#TTS_read_field['Field Name'] =  Qt.Key_F9
#TTS_read_field['Front'] =  Qt.Key_F5
#TTS_read_field['Back'] = Qt.Key_F6
#TTS_read_field['Reading'] =  Qt.Key_F7
#TTS_read_field['Text'] = Qt.Key_F8
#all the available keys are in http://doc.trolltech.com/qtjambi-4.4/html/com/trolltech/qt/core/Qt.Key.html


#subprocessing is enabled by default
# on MS Windows XP or older, there is a bug of cutting the ending of a speech occasionally, so you may want to disable it.
#if it's disable(false), Anki will be frozen while GoogleTTS recites the speech. 
#subprocessing = False
subprocessing = True


#Language code
TTS_language = 'en'
askQuestion = 0
askSentence = 0
speech_engine = "Akapela"

sengines =[["Akapela"],["Google"]]

#Supported Languages       
# code , Language, windows charset encoding
slanguages = [['af', 'Afrikaans', 'cp1252'], #or iso-8859-1
['en', 'English',	'cp1252'], #or iso-8859-1
['cy', 'Welsh',		'iso-8859-14']]


#Address to the TTS service
TTS_ADDRESS = 'http://translate.google.com/translate_tts'
#Address to the TTS service
WORDCOUNT_ADDRESS = 'http://www.wordcount.org/dbquery.php?toFind='
######################### End of Settings ##################################
import os, subprocess, re, sys, urllib, time
from aqt import mw, utils
from anki import sound
from anki.sound import playFromText
from anki.utils import stripHTML
#from anki.facts import Fact
from subprocess import Popen, PIPE, STDOUT
from urllib import quote_plus
#from ankiqt.ui import view,facteditor,utils
from anki.hooks import wrap,addHook
from PyQt4 import QtGui,QtCore
from PyQt4.QtGui import *
from aqt.reviewer import Reviewer
from aqt.utils import tooltip
from Dictionaries import Sentence,Google
from anki.stats import CollectionStats
from aqt.stats import DeckStats


icons_dir = os.path.join(mw.pm.addonFolder(), 'color-icons')
language_generator = TTS_language

# Prepend http proxy if one is being used.  Scans the environment for
# a variable named "http_proxy" for all operating systems
# proxy code contributed by Scott Otterson
proxies = urllib.getproxies()

if len(proxies)>0 and "http" in proxies:
	proxStr = re.sub("http:", "http_proxy:", proxies['http'])
	TTS_ADDRESS = proxStr + "/" + TTS_ADDRESS


sentence = Sentence()

# mplayer for windows
if subprocess.mswindows:
	dir = os.path.dirname(os.path.abspath(sys.argv[0]))
	os.environ['PATH'] += ";" + dir
	si = subprocess.STARTUPINFO()
	try:
		si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
	except:
		# python2.7+
		si.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW


######## utils
def get_language_id(language_code):
	x = 0
	for d in slanguages:
		if d[0]==language_code:
			return x
		x = x + 1

def get_engine_id(engine_code):
	x = 0
	for d in sengines:
		if d[0]==engine_code:
			return x
		x = x + 1		

def playTTSFromText(text):
	utils.showInfo(text)
	address = []
	for match in re.findall("\[GTTS:(.*?):(.*?)\]", text, re.M|re.I):
		speakit = []
		sentence = match[1]
		sentence = re.sub("\[sound:.*?\]", "", stripHTML(sentence.replace("\n", "")).encode('utf-8'))
		if len(sentence) > 100:
			utils.showInfo(sentence)
			split1 = sentence.split('.')
			for item1 in split1:
				if len(item1) > 100:
					utils.showInfo(item1)
					split2 = sentence.split(',')
					for item2 in split2:
						if len(item2) < 100:
							speakit.append(item2)
				else:
					speakit.append(item1)
		else:
			speakit.append(sentence)
		for item in speakit:
			address.append(TTS_ADDRESS+'?tl='+match[0]+'&q='+ quote_plus(item))
	if subprocess.mswindows:
		param = ['mplayer.exe', '-ao', 'win32', '-slave', '-user-agent', "'Mozilla/5.0'"]
		param.extend(address)
		if subprocessing:
			subprocess.Popen(param, startupinfo=si, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
		else:
			subprocess.Popen(param, startupinfo=si, stdin=PIPE, stdout=PIPE, stderr=STDOUT).communicate()
	else:
		param = ['mplayer', '-slave', '-user-agent', "'Mozilla/5.0'"]
		param.extend(address)
		if subprocessing:
			subprocess.Popen(param, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
		else:
			subprocess.Popen(param, stdin=PIPE, stdout=PIPE, stderr=STDOUT).communicate()


###########  TTS_read to recite the tts on-the-fly

def TTS_read(text, language=TTS_language):
#	utils.showInfo(text)
#	text = text.decode('utf-8', 'ignore')
	text = stripHTML(text.replace("\n", "")).encode('utf-8')
#	utils.showInfo(text)
#	if text.find('Â') != -1 :
#		utils.showInfo('Found T')
#		utils.showInfo(text)
#	zzz = '\u00c2'
	text = text.replace(chr(194)," ")
#	if text.find(chr(194)) != -1 :		
#		utils.showInfo('Found T0')
#		utils.showInfo(text)
#	for c in text:
#		if ord(c) > 190 :
#			utils.showInfo('Found T1')
#			utils.showInfo(c)
#			utils.showInfo(str(ord(c)))
            	
#	address = TTS_ADDRESS+'?tl='+language+'&q='+ quote_plus(text)
	address = "http://api.ispeech.org/api/rest?apikey=8d1e2e5d3909929860aede288d6b974e&Speed=-3&format=mp3&action=convert&text="+ quote_plus(text)

	if subprocess.mswindows:
		if speech_engine == "Akapela":
			param = ['SayStatic.exe', text]
		else:
			param = ['1.bat',  quote_plus(text)]
		if subprocessing:
			subprocess.Popen(param, startupinfo=si, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
		else:
			subprocess.Popen(param, startupinfo=si, stdin=PIPE, stdout=PIPE, stderr=STDOUT).communicate()
	else:
		if speech_engine == "Akapela":
			param = ['SayStatic.exe', text]
		else:
			param = ['1.bat',  quote_plus(text)]
		if subprocessing:
			subprocess.Popen(param, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
		else:
			subprocess.Popen(param, stdin=PIPE, stdout=PIPE, stderr=STDOUT).communicate()


#################### TTS in Tool's menu

class GTTS_option_menu_Dialog(object):
	def setupUi(self, Dialog):
		Dialog.setObjectName("Dialog")
		Dialog.resize(400, 300)
		Dialog.setWindowTitle("GoogleTTS")

		buttonBox = QDialogButtonBox(Dialog);
		buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32));
		buttonBox.setOrientation(QtCore.Qt.Horizontal);
		buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel);
		verticalLayoutWidget = QtGui.QWidget(Dialog);
		verticalLayoutWidget.setGeometry(QtCore.QRect(20, 70, 357, 151));
		verticalLayout = QtGui.QVBoxLayout(verticalLayoutWidget);
		verticalLayout.setContentsMargins(0, 0, 0, 0);
		label_2 = QtGui.QLabel(verticalLayoutWidget);
		label_2.setText("Choose the language that will be used by GoogleTTS");

		verticalLayout.addWidget(label_2);

		self.combobox = QtGui.QComboBox(verticalLayoutWidget);
		self.combobox.addItems([d[1] for d in slanguages])
		self.combobox.setCurrentIndex(get_language_id(TTS_language))

		verticalLayout.addWidget(self.combobox);

#################### Speech Engine		
		label_21 = QtGui.QLabel(verticalLayoutWidget);
		label_21.setText("Choose the speech engine");

		verticalLayout.addWidget(label_21);

		self.combobox1 = QtGui.QComboBox(verticalLayoutWidget);
		self.combobox1.addItems([d[0] for d in sengines])		
		self.combobox1.setCurrentIndex(get_engine_id(speech_engine))

		verticalLayout.addWidget(self.combobox1);

#################### Speech Engine		
		label = QtGui.QLabel(verticalLayoutWidget);
		label.setText("Display options");
		label.setWordWrap(True);

		verticalLayout.addWidget(label)
		self.checkbox = QtGui.QCheckBox('Ask question',verticalLayoutWidget);
		self.checkbox.setCheckState(askQuestion);
		self.checkbox1 = QtGui.QCheckBox('Ask sentence',verticalLayoutWidget);
		self.checkbox1.setCheckState(askSentence);

		verticalLayout.addWidget(self.checkbox);
		verticalLayout.addWidget(self.checkbox1);


		label_3 = QtGui.QLabel(Dialog)
		label_3.setGeometry(QtCore.QRect(100, 10, 250, 51))
		label_3.setText("GoogleTTS")
		font = QtGui.QFont()
		font.setBold(True)
		font.setPointSize(27)
		label_3.setFont(font)
		label_4 = QtGui.QLabel(Dialog)
		label_4.setGeometry(QtCore.QRect(190, 50, 150, 17))
		label_4.setText("Version "+version)

		QtCore.QObject.connect(buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
		QtCore.QObject.connect(buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
		QtCore.QMetaObject.connectSlotsByName(Dialog)


def GTTS_option_menu():
	global TTS_language
	global speech_engine	
	global askQuestion
	global askSentence	
	d = QDialog()
	form = GTTS_option_menu_Dialog()
	form.setupUi(d)
	if d.exec_():		
		TTS_language = slanguages[form.combobox.currentIndex()][0]		
		speech_engine = sengines[form.combobox1.currentIndex()][0]
		askQuestion = form.checkbox.checkState()
		askSentence = form.checkbox1.checkState()

a = QAction(mw)
a.setText("GoogleTTS")
mw.form.menuTools.addAction(a)
mw.connect(a, SIGNAL("triggered()"), GTTS_option_menu)



####################  MP3 Mass Generator


#take a break, so we don't fall in Google's blacklist. Code contributed by Dusan Arsenijevic
def take_a_break(ndone, ntotal):      
	t = 500;
	while True:
		mw.progress.update(label="Generated %s of %s, \n sleeping for %s seconds...." % (ndone+1, ntotal, t))
		time.sleep(1)
		t = t-1
		if t==0: break



from anki.hooks import addHook


######################################### Keys and AutoRead

## Check pressed key
def newKeyHandler(self, evt):
	pkey = evt.key()
	if (self.state == 'answer' or self.state == 'question'):
		for key in TTS_read_field:
			if TTS_read_field[key] == pkey:
				TTS_read(self.card.note()[key],TTS_language)
				break
	evt.accept()

def LastSentence() :
	return sentence.getOldSentence()
	
def GetExamples(text) :
	text = stripHTML(text.replace("\n", "")).encode('utf-8')
	sen = sentence.getSentence(text)
	if len(sen) == 0 :
		param = ['ParseYourDictionary.exe', text]
		subprocess.Popen(param, startupinfo=si, stdin=PIPE, stdout=PIPE, stderr=STDOUT).communicate()	

def Example_read(text,exitme=0):
	text = stripHTML(text.replace("\n", "")).encode('utf-8')
	sen = sentence.getSentence(text)
	if len(sen) == 0 :
		if exitme == 1 :
			TTS_read("No examples. %s" % (text),TTS_language)
			return 
		param = ['ParseYourDictionary.exe', text]
		if subprocessing:
			subprocess.Popen(param, startupinfo=si, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
		else:
			subprocess.Popen(param, startupinfo=si, stdin=PIPE, stdout=PIPE, stderr=STDOUT).communicate()	
		g = Google()
		g.write(text)
		Example_read(text,1)
	else :
		TTS_read(sen,TTS_language)
		
def actionRu():
    utils.showInfo(self1.card.note()['Translation'])

def GTTSautoread(toread, automatic=automaticQuestions):
	if not sound.hasSound(toread):
		if automatic == TTS_tags_only:
			playTTSFromText(toread)
		if automatic == TTS_if_no_tag_read_whole:
			if re.findall("\[GTTS:(.*?):(.*?)\]", toread, re.M|re.I):
				playTTSFromText(toread)
			else:
				TTS_read(toread,TTS_language)

def GTTS_OnQuestion(self):
	global self1
	self1 = self
	stopSpeech()
	#utils.showInfo(self.card.model()['name'])
	self.mw.qt_tool_bar.actions()[16].setDisabled(False)
	self.mw.qt_tool_bar.actions()[17].setDisabled(True)
	self.mw.qt_tool_bar.actions()[11].setDisabled(True)
	self.mw.qt_tool_bar.actions()[10].setDisabled(True)
	self.mw.qt_tool_bar.actions()[7].setDisabled(True)
	self.mw.qt_tool_bar.actions()[8].setDisabled(True)
	self.mw.qt_tool_bar.actions()[6].setDisabled(True)
	if self.card.template()['name'] != "Translation" :
		self.mw.qt_tool_bar.actions()[14].setDisabled(True)
		if self.card.template()['name'] == "Forward" :
			self.mw.qt_tool_bar.actions()[18].setDisabled(True)
			self.mw.qt_tool_bar.actions()[16].setDisabled(True)
			self.mw.qt_tool_bar.actions()[7].setDisabled(True)
			self.mw.qt_tool_bar.actions()[10].setDisabled(False)
			self.mw.qt_tool_bar.actions()[8].setDisabled(False)
			self.mw.qt_tool_bar.actions()[6].setDisabled(False)
			Example_read(self.card.q())
		else :
			GTTSautoread(self.card.q(), automaticQuestions)
			self.mw.qt_tool_bar.actions()[7].setDisabled(False)
		self.web.eval("document.getElementById('qa').style.visibility='hidden'")

#	self.web.eval("alert(document.getElementsByTagName('BODY')[0].innerHTML)")

def GTTS_OnAnswer(self):
	stopSpeech()
	self.mw.qt_tool_bar.actions()[18].setDisabled(False)
	self.mw.qt_tool_bar.actions()[16].setDisabled(False)
	self.mw.qt_tool_bar.actions()[14].setDisabled(False)
	self.mw.qt_tool_bar.actions()[10].setDisabled(False)
	self.mw.qt_tool_bar.actions()[11].setDisabled(False)
	self.mw.qt_tool_bar.actions()[8].setDisabled(False)
	self.mw.qt_tool_bar.actions()[7].setDisabled(False)
	self.mw.qt_tool_bar.actions()[6].setDisabled(False)
	tags = mw.reviewer.card.note().stringTags()
#	utils.showInfo(mw.reviewer.card.note().stringTags())
	checked = False
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
			
	self.web.eval("document.getElementById('qa').style.visibility='visible'")
	if checked :
		self.mw.reviewer.web.eval("$('#spanTags').html('&#x2639;').show();")
		self.mw.qt_tool_bar.actions()[17].setIcon(QIcon(os.path.join(icons_dir, 'warning_red.png')))
		tooltip("Defered")
	else :
		self.mw.reviewer.web.eval("$('#spanTags').hide();")
		self.mw.qt_tool_bar.actions()[17].setIcon(QIcon(os.path.join(icons_dir, 'warning.png')))
		
	self.mw.qt_tool_bar.actions()[17].setChecked(checked)
	self.mw.qt_tool_bar.actions()[17].setDisabled(False)
	
	s = self1.card.note()['Front'] + ". " + self1.card.note()['Example']
#	if self.card.template()['name'] == "Translation" :
#		s = s + " " + self1.card.note()['Example']
#	elif self.card.template()['name'] == "Forward" :
#	else :
#	
#	stA = stripHTML(self.card.a())
#	stQ = stripHTML(self.card.q())
#	s = stA.replace(stQ,"")	
	s = s.replace(".",". ")
#	if self.card.template()['name'] == "Forward" :
#	s = self.card.note()['Front'] + ". " + s
	GTTSautoread(s, automaticAnswers)

def stopSpeech():
		try:
#			subprocess.Popen.terminate(p[0])
			param = ['KillProcess.exe']
			subprocess.Popen(param, startupinfo=si, stdin=PIPE, stdout=PIPE, stderr=STDOUT).communicate()
		except:
			pass

def showHidden():    
    self1.web.eval("document.getElementById('qa').style.visibility='visible'")

###########  WordCount_get 
def WordCount_get(text):
	text = stripHTML(text.replace("\n", " ")).encode('utf-8')
	address = WORDCOUNT_ADDRESS + quote_plus(text) + '&method=SEARCH%5FBY%5FNAME'
	response = urllib.urlopen(address) 
	if 200 == response.code :
		data = response.read() 
		b1 = data.split('&',10)
		b0 = b1[3].split('=')
		b2 = b1[2].split('=')
		utils.showInfo(str(round((float(b0[1])/float(b2[1])) * 100,2)) + "%" )
	else :
		utils.showInfo('Not found')
		
def actionCount():
#	try:
	word = self1.card.note()['Front'].lower()
	WordCount_get(word)	
	utils.showInfo(str(round(100.0 *lines.index(word.encode('utf-8')) / len(lines),2)) + "%")		
#	except:
#		pass
		
Reviewer._keyHandler = wrap(Reviewer._keyHandler, newKeyHandler, "before")
Reviewer._showQuestion = wrap(Reviewer._showQuestion, GTTS_OnQuestion, "after")
Reviewer._showAnswer  = wrap(Reviewer._showAnswer, GTTS_OnAnswer, "after")

OLD_eases = CollectionStats._eases

card_filter = ''

def NEW_eases(self):
	global card_filter
		

	self.card_filter = card_filter
	if card_filter == '' :
		return OLD_eases(self)
	lims = []
	lim = self._revlogLimit()
	if lim:
		lims.append(lim)
	if self.type == 0:
		days = 30
	elif self.type == 1:
		days = 365
	else:
		days = None
	if days is not None:
		lims.append("id > %d" % (
			(self.col.sched.dayCutoff-(days*86400))*1000))
	if lims:
		lim = "where " + " and ".join(lims)
	else:
		lim = ""
	lim += " and c.ord = %s and c.id = r.cid " % card_filter
	st = """
select (case
when r.type in (0,2) then 0
when lastIvl < 21 then 1
else 2 end) as thetype,
(case when r.type in (0,2) and ease = 4 then 3 else ease end), count() from revlog as r, cards as c %s
group by thetype, ease
order by thetype, ease""" % lim.replace("id >", "r.id >")
	return self.col.db.all(st)
	
CollectionStats._eases = NEW_eases

def ask_value() :
	global card_filter
	r = utils.getText(prompt = u'Enter CardID', default=u'0')
	num = int(r[0])
	if r[1] == 0 or num is None :
		card_filter = ''
	else :
		card_filter = r[0]
		

def myfunc(self, b) :
	if len(self.form.buttonBox.buttons()) == 2 :
		b = self.form.buttonBox.addButton(_("Filter"), QDialogButtonBox.ActionRole)
		b.connect(b, SIGNAL("clicked()"), ask_value)
		
DeckStats.loadFin = wrap(DeckStats.loadFin, myfunc)


lines = [line.strip().lower() for line in open('Book1.csv')]
line = "0"
