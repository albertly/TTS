import urllib
import re
import xml.etree.ElementTree as ET
import anki.js
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
from .downloadaudio.downloaders.downloader import AudioDownloader
from anki.utils import stripHTML
from aqt import mw, utils

version = '0.2.12 Release'

class str_cir(str):
	''' A string with a built-in case-insensitive replacement method '''
	
	def ireplace(self,old,new,count=0):
		''' Behaves like S.replace(), but does so in a case-insensitive
		fashion. '''
		pattern = re.compile(re.escape(old),re.I)
		return re.sub(pattern,new,self,count)
	 
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


class CollinsDictionaryThesaurus(AudioDownloader) :
    def __init__(self, word):
        AudioDownloader.__init__(self)
        self.data = []
        self.url = 'http://www.collinsdictionary.com/dictionary/american-thesaurus/'
        word_soup = self.get_soup_from_url(self.url + word)
        syn = word_soup.findAll(attrs={'class' : 'syn'})
        for syn_tag in syn:
            self.data.append(syn_tag.text)

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
        self.c1 = 0
        self.c2 = 0
        self.word = word
        self.data = []
        self.entity = Entity()
 #       self.feed(urllib.urlopen('http://americanheritage.yourdictionary.com/' + word).read())
        self.feed(urllib.urlopen('http://www.yourdictionary.com/' + word).read())
        
    def format(self) :         
        st = "<ul>"
        for e in self.data :
          st = st + "<li>" +  str_cir(e.meaning).ireplace(self.word, " ___ ") + "</li>"
          st = st + "<ul>"
          for ex in e.examples :
            st = st + "<li>" + str_cir(ex).ireplace(self.word, " ___ ") + "</li>"
          st = st + "</ul>" 
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
                    self.entity = Entity()
                    self.entity.setMeaning(data.strip())
       
class MerriamWebsterParser() :
	def __init__(self, word):
		self.data = []
		self.word = word
#http://www.dictionaryapi.com/api/v1/references/learners/xml/root?key=91359489-f427-4143-9465-5b3afadd3d27
		xml = urllib.urlopen('http://www.dictionaryapi.com/api/v1/references/collegiate/xml/' + word + "?key=181c71fa-4b20-4ec3-83d8-5eb06fe8bdf0").read()
#		xml = urllib.urlopen('http://www.dictionaryapi.com/api/v1/references/learners/xml/' + word + "?key=91359489-f427-4143-9465-5b3afadd3d27").read()
		root = ET.fromstring(xml)
		for child in root:
			ew = child.find('./ew')
			if ew != None and child.find('./ew').text == word :
				fl = child.find('./fl').text
				dts = child.findall('.//dt')
				data = []
				for dt in dts :
					entity = Entity()
					meaning = dt.text
					if type(dt.tail) == str : meaning = meaning + " " + dt.tail
					entity.meaning = meaning
#					print "Meaning  :",  entity.meaning
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
#						print "VI  text   :", vi.text
#						print "VI  tail   :", vi.tail
#						print "VI subTemp  text   :", subTemp.text
#						print "VI subTemp  tail   :", subTemp.tail
#						print "Full example   :", example
					fw = dt.find('fw')
					if fw != None :
						meaning = ""
						if type(fw.text) == str : meaning =  fw.text
						if type(fw.tail) == str : meaning = meaning + " " + fw.tail
						entity.meaning = entity.meaning + " " + meaning
#						print "Meaning Full  :", entity.meaning
					sx = dt.find('sx')
					if sx != None :
						meaning = ""
						if type(sx.text) == str : meaning =  sx.text
						if type(sx.tail) == str : meaning = meaning + " " + sx.tail
						entity.meaning = entity.meaning + " " + meaning
#						print "Meaning Full  :", entity.meaning
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
		
class DictionaryParser() :
	def __init__(self, word):
		self.word = word

	def format(self) :
		merriamWebster = MerriamWebsterParser(self.word)
		yourDictionary = YourDictionaryParser(self.word)
		coll = CollinsDictionaryThesaurus(self.word)
		#html = "<h3><img src='http://www.yourdictionary.com/favicon.ico'>&nbsp;YourDictionary</h3>" + yourDictionary.format() + "<hr/>" + "<h3><img src='http://www.merriam-webster.com/favicon.ico'>&nbsp;Merriam-Webster</h3>" +  merriamWebster.format() + "<hr>" + coll.format()
		html ="""
<!doctype html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<title></title>
	<link rel="stylesheet" href="http://code.jquery.com/ui/1.10.1/themes/base/jquery-ui.css">
	<script>%s</script>
	<script>%s</script>
	<style type="text/css">	
		.ui-accordion-icons .ui-accordion-header a { padding-left: 2.2em; }
		.ui-accordion .ui-accordion-header .ui-icon { position: absolute; left: .5em; top: %s; margin-top: -8px; }
	</style>
</head>
<body>""" % (anki.js.jquery, anki.js.ui, '50%')

		html += "<div class='accordion'><h3><a class='f' href='#'><img src='http://www.collinsdictionary.com/favicon.ico'>&nbsp;Collins Thesaurus</a></h3>"
		html += "<div>" + coll.format() + "</div></div>"
		
		html += "<div class='accordion'><h3><a href='#'><img src='http://www.yourdictionary.com/favicon.ico'>&nbsp;YourDictionary</a></h3>"
		html += "<div>" + yourDictionary.format() + "</div></div>"
		
		html += "<div class='accordion'><h3><a href='#'><img src='http://www.merriam-webster.com/favicon.ico'>&nbsp;Merriam-Webster</a></h3>"
		html += "<div>" + merriamWebster.format() + "</div></div>"
		
		html += """
<script type="text/javascript">
    $(".accordion").accordion({ collapsible: true, active: false, heightStyle: 'content' });
	$( ".f" ).click();
</script>
 
</body>
		"""
		return html
		
