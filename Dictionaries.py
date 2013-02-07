iimport urllib
import re
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
import xml.etree.ElementTree as ET

class str_cir(str):
	''' A string with a built-in case-insensitive replacement method '''
	
	def ireplace(self,old,new,count=0):
		''' Behaves like S.replace(), but does so in a case-insensitive
		fashion. '''
		pattern = re.compile(re.escape(old),re.I)
		return re.sub(pattern,new,self,count)
	    
class Entity() :
    def __init__(self) :
        self.meaning = ""
        self.examples = []
    def setMeaning(self, meaning) :
        self.meaning = meaning
    def setExample(self, example) :
        self.examples.append(example)
        
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
            self.entity = Entity()
            self.entity.setMeaning(data)
        
class MerriamWebsterParser() :
	def __init__(self, word):
		self.data = []
		self.word = word
		self.words = []
#http://www.dictionaryapi.com/api/v1/references/learners/xml/root?key=91359489-f427-4143-9465-5b3afadd3d27
		xml = urllib.urlopen('http://www.dictionaryapi.com/api/v1/references/collegiate/xml/' + word + "?key=181c71fa-4b20-4ec3-83d8-5eb06fe8bdf0").read()
		root = ET.fromstring(xml)
		for child in root:
			if child.find('./ew').text == word :
				childrens = child.findall('*/dt')
				self.words = self.words + childrens
				print "hild     :", child.text, child.tag, child.attrib, child.find('./ew').text
				for w in childrens :
					entity = Entity()
					meaning = w.text
					if type(w.tail) == str : meaning = meaning + " " + w.tail
					entity.meaning = meaning
					print "Meaning  :", w.tag, w.text
					for c in w :
						if c.tag == 'vi' :
							example = c.text
							if type(c.tail) == str : example = example + " " + c.tail
							entity.setExample(example)
							print "ex     :", c.text    
						elif c.tag == 'fw' :
							meaning = c.text
							if type(c.tail) == str : meaning = meaning + " " + c.tail
							entity.meaning = entity.meaning + " " + meaning
							print "MeaningA  :", c.tag, c.text, c.tail
						else :
							print "MeaningR  :", c.tag, c.text, c.tail
					self.data.append(entity)
					
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
	def format1(self) :
		for w in self.words :
			print "Meaning    :", w.text, w.tail, w.tag
			for c in w :
			      print "Meanin1    :", c.text, c.tail, c.tag 

