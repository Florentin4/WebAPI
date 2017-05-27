import xml.sax

class MyHandler(xml.sax.ContentHandler):
	def __init__(self):
		self.isArticle = False # si on est dans une balise xml article
		self.isAuthor = False # si on est dans une balise xml author
		self.isTitle = False # si on est dans une balise xml title
		self.isYear = False # si on est dans une balise xml year
		self.isJournal = False # si on est dans une balise xml journal
		self.isBookTitle = False # si on est dans une balise xml booktitle
		self.publication = [] # liste de dictionnaire contenant toutes les publications. Le dictionnaire c'est pour stocker toutes les données qu'on récupère dans les balises xml 
		self.article = {} # dictionnaire contenant les données d'un article
		self.champs = ["author", "title", "year", "journal", "booktitle"] # champs ou clés du dictionnaire article
		self.data = "" # données récupéré dans le fichier xml
	
	def startElement(self, name, attrs): # éxécuté lorsqu'on lit une balise xml ouvrante. On initialise la variable booléenne afin de déterminer dans quel balise on se trouve.
		if name == "article":
			self.isArticle = True
		elif name == "author":
			self.isAuthor = True
		elif name == "title":
			self.isTitle = True
		elif name == "year":
			self.isYear = True
		elif name == "journal":
			self.isJournal = True
		elif name == "booktitle":
			self.isBookTitle = True
		
	def endElement(self, name): # éxécuté lorsqu'on lit une balise xml fermante. On met à jour les champs du dictionnaire article. Si on lit la balise xml article fermante, alors on ajoute le dictionnaire article dans la liste publication. Puis, on réinitialise les variables utilisé.
		if name == "article":
			self.publication.append(self.article)
			self.isArticle = False
			self.article = {}
		elif name == "author":
			try:
				obj2 = self.article[self.champs[0]]
				obj2.append(self.data)
				self.article.update({self.champs[0]: obj2})
			except:
				self.article.update({self.champs[0]: [self.data]})
				
			self.isAuthor = False
			self.data = ""
		elif name == "title":
			try:
				obj2 = self.article[self.champs[1]]
				obj2.append(self.data)
				self.article.update({self.champs[1]: obj2})
			except:
				self.article.update({self.champs[1]: [self.data]})
			self.isTitle = False
			self.data = ""
		elif name == "year":
			try:
				obj2 = self.article[self.champs[2]]
				obj2.append(self.data)
				self.article.update({self.champs[2]: obj2})
			except:
				self.article.update({self.champs[2]: [self.data]})
			self.isYear = False
			self.data = ""
		elif name == "journal":
			try:
				obj2 = self.article[self.champs[3]]
				obj2.append(self.data)
				self.article.update({self.champs[3]: obj2})
			except:
				self.article.update({self.champs[3]: [self.data]})
			self.data = ""
			self.isJournal = False
		elif name == "booktitle":
			try:
				obj2 = self.article[self.champs[4]]
				obj2.append(self.data)
				self.article.update({self.champs[4]: obj2})
			except:
				self.article.update({self.champs[4]: [self.data]})
			self.data = ""
			self.isBookTitle = False

	def characters(self, content): # éxécuté lorsqu'on lit les données d'une balise xml. On concatène les caractères lus avec la variable data.
		if self.isAuthor:
			self.data = self.data + content
		elif self.isTitle:
			self.data = self.data + content
		elif self.isYear:
			self.data = self.data + content
		elif self.isJournal:
			self.data = self.data + content
		elif self.isBookTitle:
			self.data = self.data + content
