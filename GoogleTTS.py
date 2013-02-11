# -*- coding: utf-8 -*-
# Author:  Arthur Helfstein Fragoso
# Email: arthur@life.net.br
# Based on: "hello-world plugin", "aprendiendoTTS" and "Japanese Support"
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
#   GoogleTTS plugin for Anki 2.0
version = '0.2.6 Release'
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
#######################################
#
# Some personal recomendation:
# I encourage you to watch the documentary movie: "Zeitgeist: Moving Forward"
# It's probably the most important movie you could ever watch.
# http://www.youtube.com/watch?v=4Z9WVZddH9w
#
# I also recommend a website to live your live to the full potential:
# http://www.highexistence.com/
#
########################### Settings #######################################
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

# quote (encode) special characters for mp3 file names:
# Windows users should have their mp3 files quoted (True), if you want to try, the system encoding should be the same as the language you are learning. and in the Table slanguage, the right charset should be set there. (it may not work, do this only if you know what you are doing. If you want it really want it, install Linux! :D
# Unix users don't need to quote (encode) special characters. so you can set it as False if you want.
# it will work alright sync with AnkiMobile, but it won't work with AnkiWeb
quote_mp3 = True	# spC3A9cial.mp3 E381AFE38184.mp3 E4BDA0E5A5BD.mp3
#quote_mp3 = False  # spécial.mp3 はい.mp3　你好.mp3


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
['sq', 'Albanian',	'cp1250'], #or iso 8859-16
['ar', 'Arabic',	'cp1256'], #or iso-8859-6
['hy', 'Armenian',	'armscii-8'],
['ca', 'Catalan',	'cp1252'], #or iso-8859-1
['zh', 'Chinese',	'cp936'],
['hr', 'Croatian',	'cp1250'], #or iso-8859-2
['cs', 'Czech',		'cp1250'], #or iso-8859-2
['da', 'Danish',	'cp1252'], #or iso-8859-1
['nl', 'Dutch',		'cp1252'], #or iso-8859-1
['en', 'English',	'cp1252'], #or iso-8859-1
['fi', 'Finnish',	'cp1252'], #or iso-8859-1
['fr', 'French',	'cp1252'], #or iso-8859-1
['de', 'German',	'cp1252'], #or iso-8859-1
['el', 'Greek',		'cp1253'], #or iso-8859-7
['ht', 'Haitian Creole','cp1252'], #or iso-8859-1
['hi', 'Hindi',		'cp1252'], #or iso-8859-1
['hu', 'Hungarian',	'cp1250'], #or iso-8859-2
['is', 'Icelandic',	'cp1252'], #or iso-8859-1
['id', 'Indonesian'],
['it', 'Italian',	'cp1252'], #or iso-8859-1
['ja', 'Japanese',	'cp932'], #or shift_jis, iso-2022-jp, euc-jp
['ko', 'Korean',	'cp949'], #or euc-kr
['la', 'Latin'],
['lv', 'Latvian',	'cp1257'], #or iso-8859-13
['mk', 'Macedonian',	'cp1251'], #iso-8859-5
['no', 'Norwegian',	'cp1252'], #or iso-8859-1
['pl', 'Polish',	'cp1250'], #or iso-8859-2
['pt', 'Portuguese',	'cp1252'], #or iso-8859-1
['ro', 'Romanian',	'cp1250'], #or iso-8859-2
['ru', 'Russian',	'cp1251'], #or koi8-r, iso-8859-5
['sr', 'Serbian',	'cp1250'], # cp1250 for latin, cp1251 for cyrillic
['sk', 'Slovak',	'cp1250'], #or iso-8859-2
['es', 'Spanish',	'cp1252'], #or iso-8859-1
['sw', 'Swahili',	'cp1252'], #or iso-8859-1
['sv', 'Swedish',	'cp1252'], #or iso-8859-1
['tr', 'Turkish',	'cp1254'], #or iso-8859-9
['vi', 'Vietnamese',	'cp1258'],
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

language_generator = TTS_language
file_max_length = 255 # Max filename length for Unix

# Prepend http proxy if one is being used.  Scans the environment for
# a variable named "http_proxy" for all operating systems
# proxy code contributed by Scott Otterson
proxies = urllib.getproxies()

if len(proxies)>0 and "http" in proxies:
	proxStr = re.sub("http:", "http_proxy:", proxies['http'])
	TTS_ADDRESS = proxStr + "/" + TTS_ADDRESS




# mplayer for windows
if subprocess.mswindows:
	file_max_length = 100 #guess of a filename max length for Windows (filename +path = 255)
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
	text = re.sub("\[sound:.*?\]", "", stripHTML(text.replace("\n", "")).encode('utf-8'))
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
            	
	address = TTS_ADDRESS+'?tl='+language+'&q='+ quote_plus(text)
	if subprocess.mswindows:
		if speech_engine == "Akapela":
			param = ['SayStatic.exe', text]
		else:
			param = ['mplayer.exe', '-ao', 'win32', '-slave', '-user-agent', "'Mozilla/5.0'", address]
		if subprocessing:
			subprocess.Popen(param, startupinfo=si, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
		else:
			subprocess.Popen(param, startupinfo=si, stdin=PIPE, stdout=PIPE, stderr=STDOUT).communicate()
	else:
		if speech_engine == "Akapela":
			param = ['SayStatic.exe', text]
		else:
			param = ['mplayer', '-slave', '-user-agent', "'Mozilla/5.0'", address]
		if subprocessing:
			subprocess.Popen(param, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
		else:
			subprocess.Popen(param, stdin=PIPE, stdout=PIPE, stderr=STDOUT).communicate()



###################  TTS_record to generate MP3 files

def TTS_record(text, language=TTS_language):
	text = re.sub("\[sound:.*?\]", "", stripHTML(text.replace("\n", "")).encode('utf-8'))
	address = TTS_ADDRESS+'?tl='+language+'&q='+ quote_plus(text)
	if quote_mp3: #re.sub removes \/:*?"<>|[]. from the file name
		file = quote_plus(re.sub('[\\\/\:\*\?"<>|\[\]\.]*', "",text)).replace("%", "")+'.mp3'
		if len(file) > file_max_length:
			file = file[0:file_max_length-4] +'.mp3'
	else:
		file = re.sub('[\\\/\:\*\?"<>|\[\]\.]*', "",text)+'.mp3'
		if len(file) > file_max_length:
			file = file[0:file_max_length-4] +'.mp3'
		if subprocess.mswindows:
			file = file.decode('utf-8').encode(slanguages[get_language_id(language)][2])
	if subprocess.mswindows:
		subprocess.Popen(['mplayer.exe', '-ao', 'win32', '-slave', '-user-agent', "'Mozilla/5.0'", address, '-dumpstream', '-dumpfile', file], startupinfo=si, stdin=PIPE, stdout=PIPE, stderr=STDOUT).wait()
		if not quote_mp3:
			return file.decode(slanguages[get_language_id(language)][2])
	else:
		subprocess.Popen(['mplayer', '-slave', '-user-agent', "'Mozilla/5.0'", address, '-dumpstream', '-dumpfile', file], stdin=PIPE, stdout=PIPE, stderr=STDOUT).wait()
	return file.decode('utf-8')



############################ MP3 File Generator


class Ui_Dialog1(object):
	def setupUi(self, Dialog):
		Dialog.setObjectName("Dialog")
		Dialog.resize(400, 300)
		Dialog.setWindowTitle("GoogleTTS :: MP3 File Generator")
		self.gridLayout = QtGui.QGridLayout(Dialog)
		self.gridLayout.setContentsMargins(10, 10, 10, 10)
		self.comboboxlabel = QtGui.QLabel(Dialog)
		self.comboboxlabel.setText("Language:")
		self.combobox = QtGui.QComboBox()
		self.combobox.addItems([d[1] for d in slanguages])
		self.combobox.setCurrentIndex(get_language_id(language_generator))
		self.textEditlabel = QtGui.QLabel(Dialog)
		self.textEditlabel.setText("Text:")
		self.charleft = QtGui.QLabel(Dialog)
		self.charleft.setText("Characters left: 100")
		self.charleft.setToolTip(_("GoogleTTS can read up to 100 characters, no more than that, sorry :'("))
		self.textEdit = QtGui.QTextEdit(Dialog)
		self.textEdit.setAcceptRichText(False)
		self.textEdit.setObjectName("textEdit")

		self.gridLayout.addWidget(self.comboboxlabel, 0, 0, 1, 1)
		self.gridLayout.addWidget(self.combobox, 1, 0, 1, 1)
		self.gridLayout.addWidget(self.textEditlabel, 0, 1, 1, 1)
		self.gridLayout.addWidget(self.charleft, 0, 2, 1, 1)
		self.gridLayout.addWidget(self.textEdit, 1, 1, 1, 2)
		self.buttonBox = QtGui.QDialogButtonBox(Dialog)
		self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
		self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)
		self.buttonBox.setObjectName("buttonBox")
		self.gridLayout.addWidget(self.buttonBox, 3, 1, 1, 3)
		self.previewbutton = QtGui.QPushButton(Dialog)
		self.previewbutton.setObjectName("preview")
		self.previewbutton.setText("Preview")
		self.gridLayout.addWidget(self.previewbutton, 2, 1, 1, 2)

		QtCore.QObject.connect(self.textEdit, QtCore.SIGNAL("textChanged()"), lambda self=self: self.charleft.setText("Characters left: "+ str(100-len(unicode(self.textEdit.toPlainText()).encode('utf-8')))))
		QtCore.QObject.connect(self.previewbutton, QtCore.SIGNAL("clicked()"), lambda self=self: TTS_read(unicode(self.textEdit.toPlainText()), slanguages[self.combobox.currentIndex()][0]))
		QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
		QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
		QtCore.QMetaObject.connectSlotsByName(Dialog)


def GTTS_Factedit_button(self):
	global language_generator
	d = QDialog()
	form = Ui_Dialog1()
	form.setupUi(d)

	if d.exec_():
		language_generator = slanguages[form.combobox.currentIndex()][0]
		file = TTS_record(unicode(form.textEdit.toPlainText()), language_generator)
		self.addMedia(file)

def GTTS_Fact_edit_setupFields(self):
	GoogleTTS = QPushButton(self.widget)
	GoogleTTS.setFixedHeight(20)
	GoogleTTS.setFixedWidth(20)
	GoogleTTS.setCheckable(True)
	GoogleTTS.connect(GoogleTTS, SIGNAL("clicked()"), lambda self=self: GTTS_Factedit_button(self))
	GoogleTTS.setIcon(QIcon(":/icons/speaker.png"))
	GoogleTTS.setToolTip(_("GoogleTTS :: MP3 File Generator"))
	GoogleTTS.setShortcut(_("Ctrl+g"))
	GoogleTTS.setFocusPolicy(Qt.NoFocus)
	#GoogleTTS.setEnabled(False)
	self.iconsBox.addWidget(GoogleTTS)
	GoogleTTS.setStyle(self.plastiqueStyle)


addHook("setupEditorButtons", GTTS_Fact_edit_setupFields)


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


srcField = -1
dstField = -1
generate_sound_tags = True


class GTTS_mp3_mass_generator_Dialog(object):
	def setupUi(self, Dialog):
		Dialog.setObjectName("Dialog")
		Dialog.resize(400, 300)
		Dialog.setWindowTitle("GoogleTTS :: MP3 Mass Generator")

		buttonBox = QDialogButtonBox(Dialog);
		buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32));
		buttonBox.setOrientation(QtCore.Qt.Horizontal);
		buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel);
		verticalLayoutWidget = QtGui.QWidget(Dialog);
		verticalLayoutWidget.setGeometry(QtCore.QRect(20, 70, 357, 171));
		verticalLayout = QtGui.QVBoxLayout(verticalLayoutWidget);
		verticalLayout.setContentsMargins(0, 0, 0, 0);
		label_2 = QtGui.QLabel(verticalLayoutWidget);
		label_2.setText("GoogleTTS will generate MP3 files to all selected facts.");

		verticalLayout.addWidget(label_2);

		self.fieldlist = []
		for f in mw.col.models.all():
			for a in f['flds']:
				self.fieldlist.append(a['name'])

		formLayoutWidget = QtGui.QWidget(Dialog)
		formLayoutWidget.setGeometry(QtCore.QRect(20, 60, 329, 118));
		formLayout = QtGui.QFormLayout(formLayoutWidget);
		#formLayout.setFieldGrowthPolicy(QFormLayout::AllNonFixedFieldsGrow);
		formLayout.setContentsMargins(0, 0, 0, 0);



		languageLabel = QtGui.QLabel(formLayoutWidget)
		languageLabel.setText("Language")
		formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, languageLabel)
		self.languageComboBox = QtGui.QComboBox(formLayoutWidget)
		self.languageComboBox.addItems([d[1] for d in slanguages])
		self.languageComboBox.setCurrentIndex(get_language_id(TTS_language))
		formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.languageComboBox)


		sourceFieldLabel = QtGui.QLabel(formLayoutWidget)
		sourceFieldLabel.setText("Source Field")
		formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, sourceFieldLabel)
		self.sourceFieldComboBox = QtGui.QComboBox(formLayoutWidget)
		self.sourceFieldComboBox.addItems([d for d in self.fieldlist])
		self.sourceFieldComboBox.setCurrentIndex(srcField)
		formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.sourceFieldComboBox)


		destinationFieldLabel = QtGui.QLabel(formLayoutWidget)
		destinationFieldLabel.setText("Destination Field")
		formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, destinationFieldLabel)
		self.destinationFieldComboBox = QtGui.QComboBox(formLayoutWidget)
		self.destinationFieldComboBox.addItems([d for d in self.fieldlist])
		self.destinationFieldComboBox.setCurrentIndex(dstField)
		formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.destinationFieldComboBox)


		self.checkBox = QtGui.QCheckBox(Dialog)
		self.checkBox.setText("Generate sound file path within the [sound:] tag.")
		if generate_sound_tags:
			self.checkBox.setChecked(True)

		label = QtGui.QLabel(verticalLayoutWidget);
		label.setText("It will overwrite anything in the Destination Field. Make sure to select the right field. It may take a while.");
		label.setWordWrap(True);

		verticalLayout.addWidget(formLayoutWidget);
		verticalLayout.addWidget(self.checkBox);
		verticalLayout.addWidget(label);

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

#take a break, so we don't fall in Google's blacklist. Code contributed by Dusan Arsenijevic
def take_a_break(ndone, ntotal):      
	t = 500;
	while True:
		mw.progress.update(label="Generated %s of %s, \n sleeping for %s seconds...." % (ndone+1, ntotal, t))
		time.sleep(1)
		t = t-1
		if t==0: break

def generate_audio_files(factIds, language, srcField_name, dstField_name, generate_sound_tags):
	returnval = {'fieldname_error': 0}
	nelements = len(factIds)
	batch = 900
	for c, id in enumerate(factIds):
		if (c+1)%batch == 0:
			take_a_break(c, nelements)
		note = mw.col.getNote(id)

		if not (srcField_name in note.keys() and dstField_name in note.keys()):
			returnval['fieldname_error'] += 1
			continue

		mw.progress.update(label="Generating MP3 files...\n%s of %s\n%s" % (c+1, nelements,note[srcField_name]))

		if generate_sound_tags:
			note[dstField_name] = '[sound:'+ TTS_record(note[srcField_name], language) +']'
		else:
			note[dstField_name] = TTS_record(note[srcField_name], language)
		print note[dstField_name]
		note.flush()

	return returnval


def setupMenu(editor):
	a = QAction("GoogleTTS MP3 Mass Generator", editor)
	editor.form.menuEdit.addAction(a)
	editor.connect(a, SIGNAL("triggered()"), lambda e=editor: onGenerate(e))


def onGenerate(self):
	global TTS_language, dstField, srcField, generate_sound_tags
	sf = self.selectedNotes()
	if not sf:
		utils.showInfo("Select the notes and then use the MP3 Mass Generator")
		return
	import anki.find
	fields = sorted(anki.find.fieldNames(self.col, downcase=False))
	d = QDialog(self)
	frm = GTTS_mp3_mass_generator_Dialog()
	frm.setupUi(d)
	d.setWindowModality(Qt.WindowModal)

	if not d.exec_():
		return

	srcField = frm.sourceFieldComboBox.currentIndex()
	dstField = frm.destinationFieldComboBox.currentIndex()
	languageField = frm.languageComboBox.currentIndex()

	if srcField == -1 or dstField == -1 :
		return

	self.mw.checkpoint(_("GoogleTTS MP3 Mass Generator"))
	self.mw.progress.start(immediate=True, label="Generating MP3 files...")

	self.model.beginReset()

	result = generate_audio_files(sf, slanguages[languageField][0], frm.fieldlist[srcField], frm.fieldlist[dstField], generate_sound_tags)

	self.model.endReset()
	self.mw.progress.finish()
	nupdated = len(sf) - result['fieldname_error']
	utils.showInfo((ngettext(
		"%s note updated",
		"%s notes updated", nupdated) % (nupdated))+  

		((ngettext(
		"\n%s fieldname error. A node doesn't have the Source Field '%s' or the Destination Field '%s'",
		"\n%s fieldname error. Those nodes don't have the Source Field '%s' or the Destination Field '%s'", result['fieldname_error'])
		% (result['fieldname_error'], frm.fieldlist[srcField], frm.fieldlist[dstField])) if result['fieldname_error'] > 0 else "")
		)

from anki.hooks import addHook
addHook("browser.setupMenus", setupMenu)


######################################### Keys and AutoRead
def newKeyHandler1(self):
    return
#    utils.showInfo("1")
#    self.web.eval("alert(document.getElementsByTagName('BODY')[0].innerHTML)")

## Check pressed key
def newKeyHandler(self, evt):
	pkey = evt.key()
	if (self.state == 'answer' or self.state == 'question'):
		for key in TTS_read_field:
			if TTS_read_field[key] == pkey:
				TTS_read(self.card.note()[key],TTS_language)
				break
	evt.accept()

def Example_read(text):
	text = re.sub("\[sound:.*?\]", "", stripHTML(text.replace("\n", "")).encode('utf-8'))
	param = ['ParseYourDictionary.exe', text]
	if subprocessing:
		subprocess.Popen(param, startupinfo=si, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
	else:
		subprocess.Popen(param, startupinfo=si, stdin=PIPE, stdout=PIPE, stderr=STDOUT).communicate()	

def actionRu():
    utils.showInfo(self1.card.note()['Translation'])

def GTTSautoread(toread, automatic):
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
	time.sleep(1)
	#utils.showInfo(self.card.model()['name'])
	self.mw.qt_tool_bar.actions()[16].setDisabled(False)
	self.mw.qt_tool_bar.actions()[17].setDisabled(True)
	if self.card.template()['name'] != "Translation" :
		if self.card.template()['name'] == "Forward" :
			self.mw.qt_tool_bar.actions()[16].setDisabled(True)
			Example_read(self.card.q())
		else :
			GTTSautoread(self.card.q(), automaticQuestions)
		self.web.eval("document.getElementById('qa').style.visibility='hidden'")

#	self.web.eval("alert(document.getElementsByTagName('BODY')[0].innerHTML)")

def GTTS_OnAnswer(self):
	stopSpeech()
	time.sleep(1)	
	self.mw.qt_tool_bar.actions()[16].setDisabled(False)
	
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
			
	self.mw.qt_tool_bar.actions()[17].setChecked(checked)
	self.mw.qt_tool_bar.actions()[17].setDisabled(False)
	
	self.web.eval("document.getElementById('qa').style.visibility='visible'")
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
	text = re.sub("\[sound:.*?\]", "", stripHTML(text.replace("\n", " ")).encode('utf-8'))
	address = WORDCOUNT_ADDRESS + quote_plus(text) + '&method=SEARCH%5FBY%5FNAME'
	response = urllib.urlopen(address) 
	data = response.read() 
	b1 = data.split('&',10)
	b0 = b1[3].split('=')
	b2 = b1[2].split('=')
	utils.showInfo(str(round((float(b0[1])/float(b2[1])) * 100,2)) + "%" )
	
def actionCount():
#	try:
	word = self1.card.note()['Front'].lower()
	WordCount_get(word)	
	utils.showInfo(str(round(100.0 *lines.index(word.encode('utf-8')) / len(lines),2)) + "%")		
#	except:
#		pass
		
Reviewer._showQuestion = wrap(Reviewer._showQuestion, newKeyHandler1, "before")
Reviewer._keyHandler = wrap(Reviewer._keyHandler, newKeyHandler, "before")
Reviewer._showQuestion = wrap(Reviewer._showQuestion, GTTS_OnQuestion, "after")
Reviewer._showAnswer  = wrap(Reviewer._showAnswer, GTTS_OnAnswer, "after")

lines = [line.strip().lower() for line in open('Book1.csv')]
line = "0"
