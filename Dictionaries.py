import os
import urllib
import urllib2
import re
import xml.etree.ElementTree as ET
import anki.js
import codecs
from random import randint
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
from .downloadaudio.downloaders.downloader import AudioDownloader
from anki.utils import stripHTML, json
from aqt import mw, utils
import json
version = '0.2.38 Release'

def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

class Google() :
	def write(self,word) :
		content = []
		fullname = Storage(word).getPath() + word + ".bin.txt"
		try :
			with open(fullname, 'r') as f: content = f.readlines()
		except IOError :
			pass
		#url = u'http://translate.google.com//translate_a/ex?sl=en&tl=ru&q=' + word
		url = u'http://translate.google.com//translate_a/single?client=t&sl=en&tl=ru&dt=ex&q=' + word
		user_agent = 'Mozilla/5.0'
		request = urllib2.Request(url)
		request.add_header('User-agent', user_agent)
		response = urllib2.urlopen(request)
		if response.code == 200 :
			s = response.read()
			if len(s) < 20 :
				return
			s = s.replace("[,,,,,,,,,,,,,[", "")
			s = s.replace("]]]]", "]]")
			s = s.replace(",,", ",\"\",")
			s = s.replace(",,", ",\"\",")
			#utils.showInfo(s)
			#utils.showInfo(s[2500:])
			j = json.loads(s)
			l = 0 
			try :
				l = len(j)
			except IndexError :
				pass
				
			if l > 0 :
				with open(fullname, "a") as f1:
					for s in j :
						st = stripHTML(removeNonAscii(s[0])) + "\n"
						try :
							if not st in content :
								f1.write(st)
						except:
							utils.showInfo(word)
							break




class Sentence() :
	def __init__(self) :
		self.word = ''
		self.content = []
		self.sentence = ''
		self.rand = -1
	
	def clean(self) :
		self.content = []
		self.sentence = ''
		self.rand = -1
		
	def getOldSentence(self) :
		return self.sentence
		
	def getSentence(self, word) :
		sentence = ''
		fullname = Storage(word).getPath() + word + ".bin.txt"
		try :
			if word != self.word or len(self.content) == 0:
				with open(fullname, 'r') as f: self.content = f.readlines()
				self.word = word
				self.rand = -1
			length = len(self.content)
			if length != 0 :
				while True :
					rand = randint(0,length-1)
					if rand != self.rand or length == 1 :
						self.rand = rand
						break
				sentence = self.content[self.rand].strip()
				self.sentence = sentence
			else :
				self.clean()
				
		except IOError :
			self.clean()
			pass
		
		return sentence
		
class Storage() :
	base = 'c:/users/albert/AppData/Roaming/ParseYourDictionary/ParseYourDictionary/1.0.0.0/'
	def __init__(self, word) :
		self.word = word
		
	def getPath(self) :
		storagePath = Storage.base + self.word[:2] + '/'
		
		try :
			os.makedirs(storagePath)
		except OSError:
			pass
		
		return storagePath
	
class str_cir(str):
	''' A string with a built-in case-insensitive replacement method '''

	def ireplace(self,old,new,count=0):
		''' Behaves like S.replace(), but does so in a case-insensitive
		fashion. '''
		pattern = re.compile(re.escape(old),re.I)
		str = re.sub(pattern,new,self,count)
		
		pattern = re.compile(re.escape(old[0:-1]),re.I)
		str = re.sub(pattern,new,str,count)
		return str

class GroupEntities() :
	def __init__(self, data, fl) :
		self.entities = data
		self.fl = fl

class Entity() :
    def __init__(self) :
        self.meaning = ""
        self.examples = []
    def setMeaning(self, meaning) :
        self.meaning = meaning
    def setExample(self, example) :
        self.examples.append(example)
    

    def dumps(self) :
        json_meaning = json.dumps(self.meaning)
        json_examples = json.dumps(self.examples)
        json_entity = json.dumps([json_meaning, json_examples])
        return json_entity
    
    def loads(self, json_entity) :
        arr_entity = json.loads(json_entity)
        self.meaning = json.loads(arr_entity[0])
        self.examples = json.loads(arr_entity[1])

class EntityEx(Entity) :
    def __init__(self) :
        Entity.__init__(self)
        self.sub = False

    def dumps(self) :
        json_meaning = json.dumps(self.meaning)
        json_examples = json.dumps(self.examples)
        json_sub = json.dumps(self.sub)
        json_entity = json.dumps([json_meaning, json_examples, json_sub])
        return json_entity
    
    def loads(self, json_entity) :
        arr_entity = json.loads(json_entity)
        self.meaning = json.loads(arr_entity[0])
        self.examples = json.loads(arr_entity[1])
        self.sub = json.loads(arr_entity[2])
        
class CollinsDictionaryCommonness(AudioDownloader) :
    def __init__(self, word):
        self.data = ''
        self.word = word
        AudioDownloader.__init__(self)
        self.icon_url = 'http://www.collinsdictionary.com/'
        self.url = 'http://www.collinsdictionary.com/dictionary/american/'
        if not self.load() :
           word_soup = self.get_soup_from_url(self.url + word)
           commonness = word_soup.find(attrs={'class' : 'commonness_image'})
           if commonness != None :
              self.data = commonness.prettify()
              if len(self.data) > 0 :
                 self.dump()

    def format(self) :
        return self.data.replace("<img", "<img align='right' ").replace("/static/graphics/commonnessDots/", Storage.base)

    def dump(self) :
        fp = Storage(self.word).getPath() + self.word + '.cdc'

        with open(fp, 'w') as f:
             f.write(self.data)

    def load(self) :
        fp = Storage(self.word).getPath() + self.word + '.cdc'
        if os.path.exists(fp) :
            with open(fp, 'r') as f:
                self.data = f.read()
            return True
        else :
            return False
			
class MacmillanThesaurusParser(AudioDownloader) :
    def __init__(self, word):
        AudioDownloader.__init__(self)
        self.data = []
        self.word = word
        self.stars = 0
        if not self.load() :
            self.url = 'http://www.macmillandictionary.com/thesaurus/american/'
            word_soup = self.get_soup_from_url(self.url + word)
            HOMOGRAPH = word_soup.find(attrs={'class' : 'HOMOGRAPH'})
            if HOMOGRAPH == None : return
            stars = HOMOGRAPH.findAll('img')
            if stars != None :
                self.stars = len(stars)

                SENSE = HOMOGRAPH.findAll(attrs={'class' : 'SENSE-BODY'})
                if len(SENSE) == 0 : SENSE = HOMOGRAPH.findAll(attrs={'class' : 'phrasalverbsense'}) 
                for s in SENSE:
                   entity = EntityEx()
                   meaning = s.span.getText(u' ')
                   entity.setMeaning(meaning)
                   cattitle = s.find(attrs={'class' : 'cattitle'})
                   synonyms = s.find(attrs={'class' : 'synonyms'})

                   st_cattitle = ''
                   if cattitle != None : st_cattitle = cattitle.getText() + u'&nbsp;'
                   st_synonyms = ''
                   if synonyms != None : st_synonyms = synonyms.getText().replace(",", ", ") 
                   entity.setExample(st_cattitle + st_synonyms)
                   self.data.append(entity)
                
                   SUB_SENSE_CONTENT = s.findAll(attrs={'class' : 'SUB-SENSE-CONTENT'})
                   for ss in SUB_SENSE_CONTENT :
                       entity = EntityEx()
                       entity.setMeaning(ss.span.getText(u' '))
                       cattitle = ss.find(attrs={'class' : 'cattitle'})
                       synonyms = ss.find(attrs={'class' : 'synonyms'})
   
                       st_cattitle = ''
                       if cattitle != None : st_cattitle = cattitle.getText() + u'&nbsp;'
                       st_synonyms = ''
                       if synonyms != None : st_synonyms = synonyms.getText().replace(",", ", ") 
                       entity.setExample(st_cattitle + st_synonyms)   

                       entity.sub = True
                       self.data.append(entity)   
               
                self.dump()

    def dump(self) :
        fp = Storage(self.word).getPath() + self.word + '.mtp'
        arr_data = []
        for e in self.data :
            st = e.dumps()
            arr_data.append(st)

        arr_data_all = [json.dumps(self.stars), json.dumps(arr_data)]

        with open(fp, 'w') as f:
              json.dump(arr_data_all, f)

    def load(self) :
        fp = Storage(self.word).getPath() + self.word + '.mtp'
        if os.path.exists(fp) :
            arr_data_all = []

            with open(fp, 'r') as f:
                arr_data_all = json.load(f)

            self.stars = json.loads(arr_data_all[0])
            arr_data = json.loads(arr_data_all[1])

            for st in arr_data :
                e = EntityEx()
                e.loads(st)
                self.data.append(e)   
            return True
        else :
            return False
			
    def formatStars(self) :
        st = ""
        for x in range(0, self.stars) :
            st += u"<img align='right' style='margin-top: -3px' src='" + Storage.base + u"star.gif'>"
        return st

    def format(self) :
        st = "<ul>"
        for e in self.data :
            if e.sub :
                st += "<dd>"
                margin = "40"
            else :
                st += "<li>"
                margin = "20"
            st +=  str_cir(e.meaning.encode('ascii','replace')).ireplace(self.word, " ___ ") 

            for ex in e.examples :
                st +=  "<p style='margin-left: %spx'>" % (margin) +  str_cir(ex.encode('ascii','replace')).ireplace(self.word, " ___ ") + "</p>"
            
            if e.sub :
               st +=  "</dd> "
            else :
               st += "</li>"
        st += "</ul>"    

        return st

class CollinsDictionaryThesaurus(AudioDownloader) :
    def __init__(self, word):
        AudioDownloader.__init__(self)
        self.data = []
        self.word = word
        if not self.load() :
            self.url = 'http://www.collinsdictionary.com/dictionary/american-thesaurus/'
            word_soup = self.get_soup_from_url(self.url + word)
            syn = word_soup.findAll(attrs={'class' : 'syn'})
            if len(syn) == 0 :
                self.url = 'http://www.collinsdictionary.com/dictionary/english-thesaurus/'
                word_soup = self.get_soup_from_url(self.url + word)
                syn = word_soup.findAll(attrs={'class' : 'syn'})
            something_to_dump = False
            for syn_tag in syn:
                self.data.append(syn_tag.text)
                something_to_dump = True
            if True :
                self.dump()
   
    def dump(self) :
        fp = Storage(self.word).getPath() + self.word + '.cdt'

        with open(fp, 'w') as f:
              json.dump(self.data, f)

    def load(self) :
        fp = Storage(self.word).getPath() + self.word + '.cdt'
        if os.path.exists(fp) :
            with open(fp, 'r') as f:
                self.data = json.load(f)
            return True
        else :
            return False

    def format(self) :
        st = "<span>"
        for e in self.data :
           st = st + e + ", "
        st = st + "</span>"
        return st
          

class YourDictionaryParser(HTMLParser):
    def __init__(self, word):
        HTMLParser.__init__(self)
        self.f1 = 0
        self.f2 = 0
        self.skip = 0
        self.word = word
        self.data = []
        self.entity = Entity()
        self.something_to_dump = False
        if not self.load() :
 #       http://americanheritage.yourdictionary.com/
#            self.feed(urllib.urlopen('http://www.yourdictionary.com/' + word).read())
            connection = urllib.urlopen('http://www.yourdictionary.com/' + word)
            encoding = connection.headers.getparam('charset')
            page = connection.read().decode("utf-8")
            self.feed(page)
            self.something_to_dump = True
        if self.something_to_dump : 
            self.dump()

    
    def dump(self) :
        fp = Storage(self.word).getPath() + self.word + '.ydp'
        arr_data = []
        for e in self.data :
            st = e.dumps()
            arr_data.append(st)

        with open(fp, 'w') as f:
              json.dump(arr_data, f)

    def load(self) :
        fp = Storage(self.word).getPath() + self.word + '.ydp'
        if os.path.exists(fp) :
            arr_data = []
            with open(fp, 'r') as f:
                arr_data = json.load(f)
            for st in arr_data :
                e = Entity()
                e.loads(st)
                self.data.append(e)   
            return True
        else :
            return False

    def format(self) :         
        st = "<ul>"
        for e in self.data :
          st = st + "<li>" +  str_cir(e.meaning).ireplace(self.word, " ___ ") 
#          st = st + "<ul>"
          for ex in e.examples :
            st = st + "<p style='margin-left: 20px'>" + str_cir(ex).ireplace(self.word, " ___ ") + "</p>"
          st = st + "</li>" 
        st = st + "</ul>"        

        return st
    
    def handle_starttag(self, tag, attrs):
        if tag == 'span' :
            for name, value in attrs:
                if name == 'class' and value == 'custom_entry_pos' :
                    print "     attr1:", name, value
                    self.skip = 1                
                    return
            
        if tag != 'div' :
            return
                
        for name, value in attrs:
            if name == 'class' and value == 'custom_entry' :
                print "     attr1:", name, value
                self.f1 = 1                
            elif name == 'class' and value == 'custom_entry_example':
               print "     attr2:", name, value
               self.f2 = 1                
                
    def handle_endtag(self, tag):
        if self.skip == 1 :
            self.skip = 0            
        elif self.f2 == 1 and tag == 'div' :
            print "End tag 2 :", tag
            self.f2 = 0        
        elif self.f1 == 1 and tag == 'div' :
            self.data.append(self.entity)
            print "End tag 1 :", tag
            self.f1 = 0
            
    def handle_data(self, data):
        if self.f2 == 1 :
            print "Data2     :", data
            if len(data.strip()) > 0 :
                self.entity.setExample(data)
        elif self.f1 == 1 and self.skip == 0:
            print "Data1     :", data
            if len(data.strip()) > 0 :
                    self.something_to_dump = True
                    self.entity = Entity()
                    self.entity.setMeaning(data.strip())
					
class WordNetParser() :
	def __init__(self, word):
		self.data = []
		self.word = word.strip()
		self.xml = ""
		try_dump = False
		if not self.load() :
			self.xml = urllib.urlopen('http://www.stands4.com/services/v2/syno.php?uid=2686&tokenid=WAOzklnbIIZEFAjE&word=' + self.word).read()
			try_dump = True
			
			
		try :
			root = ET.fromstring(self.xml)
		except :
			utils.showInfo(self.word)
			utils.showInfo(self.xml)
			raise
			
		for child in root:
			t = child.find('./term')
			if t == None :
				break
			else :
				if try_dump :
					self.dump()
					try_dump = False
			term = t.text
			definition = child.find('./definition').text
			p = child.find('./partofspeech')
			if p is None or p.text is None :
				partofspeech = 'A'
			else :
				partofspeech = p.text
			
			s = child.find('./synonyms')
			if (s is None or s.text is None) :
				synonyms = ''
			else :
				synonyms = s.text
			
			
			if not partofspeech[0].isupper() :
				entity = Entity()
				entity.setMeaning(definition.strip())
				synset = [x.strip() for x in (term + ", " + synonyms).split(',')]
				synset = list(set(synset))
				entity.setExample(", ".join(synset))
				self.data.append(entity)
				
	def dump(self) :
		fp = Storage(self.word).getPath() + self.word + '.wnp'

		with open(fp, 'w') as f:
			f.write(self.xml)

	def load(self) :
		fp = Storage(self.word).getPath() + self.word + '.wnp'
		if os.path.exists(fp) :
			with codecs.open(fp, 'r') as f:
				self.xml = f.read() 
			return True
		else :
			return False

	def format(self) :
		st = "<ul>"
		for e in self.data :
			st += "<li> "
			st +=    str_cir(e.meaning.encode('ascii','replace')).ireplace(self.word, " ___ ") 
			
			for ex in e.examples :
				st +=  "<p style='margin-left: 20px'>" +  str_cir(ex.encode('ascii','replace')).ireplace(self.word, " ___ ") + "</p>"
			
			st +=  "</li> "

		st += "</ul>"    

		return st
		
class MerriamWebsterThesaurusParser() :
	def __init__(self, word):
		self.data = []
		self.word = word
		self.xml = ""
		dump_me = False
		if not self.load() :
			self.xml = urllib.urlopen('http://www.dictionaryapi.com/api/v1/references/thesaurus/xml/' + word + "?key=ebaacac2-31ed-4e7a-96be-463a80ad5770").read()
			dump_me = True
			
		root = ET.fromstring(self.xml)
		for child in root:
			hw = child.find('./term/hw') #va
			found1 = hw != None and child.find('./term/hw').text == word
			if not found1 :
				va = child.find('./vr/va')
				found1 = va != None and child.find('./vr/va').text == word
			if found1 :
				if dump_me :
					self.dump()
					dump_me = False
				fl = child.find('./fl').text
				senss = child.findall('./sens')
				data = []
				for sens in senss :
					entity = Entity()
					
					mc = sens.find('./mc')
					meaning =  mc.text
					subTemp = mc.findall('./it') #italic
					for it in subTemp :
						if it != None :
							if type(it.text) == str : meaning += it.text
							if type(it.tail) == str : meaning += it.tail
					if type(mc.tail) == str : meaning += mc.tail
					entity.meaning = meaning
					
					syn = sens.find('./syn')
					#'<b>Synonyms:&nbsp;</b>'
					synonims =  sens.find('./syn').text
					subTemp = syn.findall('it') #italic
					for it in subTemp :
						if it != None :
							
							if type(it.text) == str or type(it.text) == unicode : synonims += it.text.encode('ascii','replace')
							if type(it.tail) == str or type(it.tail) == unicode : synonims += it.tail.encode('ascii','replace')
					if type(syn.tail) == str : synonims += syn.tail
					entity.examples.append(synonims)
					
					relwords = sens.find('./rel')
					if relwords != None :
						rel = '<i>Related Words:&nbsp;</i>' + relwords.text
						entity.examples.append(rel)

					self.data.append(entity)

	def dump(self) :
		fp = Storage(self.word).getPath() + self.word + '.mwt'

		with open(fp, 'w') as f:
			f.write(self.xml)

	def load(self) :
		fp = Storage(self.word).getPath() + self.word + '.mwt'
		if os.path.exists(fp) :
			with codecs.open(fp, 'r') as f:
				self.xml = f.read() 
			return True
		else :
			return False

	def format(self) :
		st = "<ul>"
		for e in self.data :
			st += "<li> "
			st +=    str_cir(e.meaning.encode('ascii','replace')).ireplace(self.word, " ___ ") 
			
			for ex in e.examples :
				st +=  "<p style='margin-left: 20px'>" +  str_cir(ex.encode('ascii','replace')).ireplace(self.word, " ___ ") + "</p>"
			
			st +=  "</li> "

		st += "</ul>"    

		return st
		
class MerriamWebsterParser() :
	def __init__(self, word):
		self.data = []
		self.word = word
		self.xml = ''
		dump_me = False
#		84ffb629-a7c3-4512-9c3c-a520c79ded19 (albert@gmail) 181c71fa-4b20-4ec3-83d8-5eb06fe8bdf0 (albertly@yandex)
		if not self.load() :
			self.xml = urllib.urlopen('http://www.dictionaryapi.com/api/v1/references/collegiate/xml/' + word + "?key=84ffb629-a7c3-4512-9c3c-a520c79ded19").read()
			dump_me = True
			
		root = ET.fromstring(self.xml)
		for child in root:
			ew = child.find('./ew')
			if ew != None and child.find('./ew').text == word :
				if dump_me :
					self.dump()
					dump_me = False
				fl = ''
				fle = child.find('./fl')
				if fle != None :
					fl = fle.text
				else :
					continue
				dts = child.findall('.//dt')
				data = []
				for dt in dts :
					entity = Entity()
					meaning = dt.text
					if type(dt.tail) == str : meaning = meaning + " " + dt.tail
					entity.meaning = meaning
					vis = dt.findall(".//vi")
					for vi in vis :
						example = ""
						if type(vi.text) == str : example = vi.text
						subTemp = vi.find('it') #italic
						if subTemp != None :
							if type(subTemp.text) == str : example = example + subTemp.text
							if type(subTemp.tail) == str : example = example + " " + subTemp.tail
						if type(vi.tail) == str : example = example + " " + vi.tail
						entity.setExample(example)

					fw = dt.find('fw')
					if fw != None :
						meaning = ""
						if type(fw.text) == str : meaning =  fw.text
						if type(fw.tail) == str : meaning = meaning + " " + fw.tail
						entity.meaning = entity.meaning + " " + meaning
					sx = dt.find('sx')
					if sx != None :
						meaning = ""
						if type(sx.text) == str : meaning =  sx.text
						if type(sx.tail) == str : meaning = meaning + " " + sx.tail
						entity.meaning = entity.meaning + " " + meaning
					data.append(entity)
				group = GroupEntities(data, fl)
				self.data.append(group)

	def format(self) :
		st = "<ul>"
		for e1 in self.data :
			st = st + "<li> " + e1.fl + "<ul>"
			for e in e1.entities :
				st = st + "<li>" +  str_cir(e.meaning).ireplace(self.word, " ___ ") + "</li>"
				st = st + "<ul>"
				for ex in e.examples :
					st = st + "<li>" + str_cir(ex).ireplace(self.word, " ___ ") + "</li>"
				st = st + "</ul>" 
			st = st + "</ul></li>"
		st = st + "</ul>"        

		return st
		
	def dump(self) :
		fp = Storage(self.word).getPath() + self.word + '.mwd'

		with open(fp, 'w') as f:
			f.write(self.xml)

	def load(self) :
		fp = Storage(self.word).getPath() + self.word + '.mwd'
		if os.path.exists(fp) :
			with codecs.open(fp, 'r') as f:
				self.xml = f.read() 
			return True
		else :
			return False
			
class DictionaryParser() :
	def __init__(self, word):
		self.word = word

	def format(self) :
		collComm =  CollinsDictionaryCommonness(self.word)
		merriamWebsterThesaurus = MerriamWebsterThesaurusParser(self.word)
		macmillanThesaurus = MacmillanThesaurusParser(self.word)
		yourDictionary = YourDictionaryParser(self.word)
		coll = CollinsDictionaryThesaurus(self.word)
		wordnet = WordNetParser(self.word)
		word = self.word
		
		class Synonims :
			def getSynonims(self) :
				l = word[:1]
				synonims = ''
				data = merriamWebsterThesaurus.data
				for e in data :
					synonims += e.examples[0] + ", "
					
#				synonims += ", "
				data = wordnet.data
				for e in data :
					synonims += e.examples[0]
					
				data = coll.data
				for st in data :
					synonims += ", " + st
				
				synset = [x.strip() for x in (synonims).split(',')]
				synset1 = []
				for s in synset :
					if s[:1] == l :  synset1.append(s)
				synset = sorted(set(synset1))
				
				return str_cir(", ".join(synset).encode('ascii','replace')).ireplace(word, " ___ ") 
				
		html ="""
<!doctype html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<title></title>
	<link rel="stylesheet" href="C:\\Users\\albert\\Documents\\Anki\\addons\\CSS\\jquery-ui-1.10.2.custom.min.css">
	<script>%s</script>
	<script>%s</script>
	<style type="text/css">	

		.ui-accordion-icons .ui-accordion-header a { padding-left: 2.2em; }
		.ui-accordion .ui-accordion-header .ui-icon { position: absolute; left: .5em; top: %s; margin-top: -8px; }
		ul { padding-left: 0px;}
		li {
				padding-left: 5px;
			}
		ul.sub { padding-left: 5px;}
		li.sub {
				padding-left: 10px;
			}
	</style>
</head>
<body>""" % (anki.js.jquery, anki.js.ui, '50%')

		html += "<div class='accordion'><h3><a class='f' href='#'><img src='" + Storage.base + "coll.ico'>&nbsp;Collins Thesaurus&nbsp;</a>" + collComm.format() + "</h3>"
		html += "<div>" + coll.format() + "</div></div>"
		
		if len(yourDictionary.data) > 0 :
			html += "<div class='accordion'><h3><a href='#'><img src='" + Storage.base + "yourDictionary.ico'>&nbsp;YourDictionary</a></h3>"
			html += "<div>" + yourDictionary.format() + "</div></div>"
			
		if len(merriamWebsterThesaurus.data) > 0 :
			html += "<div class='accordion'><h3><a href='#'><img src='" + Storage.base + "merriam.ico'>&nbsp;Merriam-Webster Thesaurus</a></h3>"
			html += "<div>" + merriamWebsterThesaurus.format() + "</div></div>"
#		else :
#			merriamWebster = MerriamWebsterParser(self.word)
#			html += "<div class='accordion'><h3><a href='#'><img src='" + Storage.base + "merriam.ico'>&nbsp;Merriam-Webster</a></h3>"
#			html += "<div>" + merriamWebster.format() + "</div></div>"

		html += "<div class='accordion'><h3><a href='#'><img src='" + Storage.base + "macmillan.ico'>&nbsp;Macmillan Thesaurus</a>" + macmillanThesaurus.formatStars() + "</h3>"
		html += "<div>" + macmillanThesaurus.format() + "</div></div>"
		
		if len(wordnet.data) > 0 :
			html += "<div class='accordion'><h3><a href='#'><img src='" + Storage.base + "wordnet.ico'>&nbsp;Word Net</a></h3>"
			html += "<div>" + wordnet.format() + "</div></div>"
		
		synonims = Synonims()
		html += "<br><hr>"
		html += "<div class='ui-widget'>" + synonims.getSynonims() + "</div>"
		html += """
<script type="text/javascript">
    $(".accordion").accordion({ collapsible: true, active: false, heightStyle: 'content' });
	$( ".f" ).click();
</script>
 
</body>
		"""
		
		return html
		


