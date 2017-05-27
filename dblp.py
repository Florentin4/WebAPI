import xml.sax
from bottle import route, run, template, request
import requests
import json
import re
from parser import *

parser = xml.sax.make_parser() # initialise la variable parser afin de pouvoir parser le fichier dblp.xml
handler = MyHandler() # initialise la variable handler comme étant un objet de la classe MyHandler
parser.setContentHandler(handler)
parser.parse(open("dblp.xml","r")) # parse le fichier xml

@route('/publications/<id:int>')
def publications(id):
	fields = "" # champs récupéré dans la route
	fields2 = [] # champs validé et récupéré dans l'attribut champs de la variable handler.
	isFields = False # si le parametre fields est présent dans la route
	errorData = '' # chaîne de caractère contenant le nom de l'erreur
	
	try: # exception lancé si le paramètre fields n'est pas spécifié dans la route.
		if request.query['fields'] != '': # si la valeur du paramètre n'est pas vide
			fields = str(request.query['fields']).split(",")
			
			# vérifie si le champs spécifié dans la route est valide par rapport au champ contenu dans les dictionnaires de l'attribut publication et récupère le nom exacte du champ.
			for i in fields: 
				for j in handler.champs: 
					if i.lower().count(j.lower()) and len(i) == len(j):
						fields2.append(j)
			
			isFields = True
		
		else :
			errorData += 'fields '
	except KeyError:
		print("KeyError")
		
	# initialise la variable res selon les cas.
	if 0 <= id < len(handler.publication) and errorData == '': # Si id compris entre 0 et taille de la liste publication et pas d'erreur.
		if not isFields: # pas de paramètre fields spécifié
			res = {'type': 'ok', 'data': handler.publication[id]}
		elif isFields and len(fields2) > 0 :
			res2 = {}
			for i in fields2: # récupère seulement pour chaque publication les champs spécifié dans fields2
				res2[i] = handler.publication[id][i]
			res = {'type': 'ok', 'data': res2}
		else :
			res = {'type': 'error', 'data': 'le champ specifie est incorrecte'}
	elif 0 <= id < len(handler.publication) and errorData != '':
		res = {'type': 'error', 'data': 'le parametre fields est indefini'}
	else :
		data = "identifiant specifie n'est pas compris entre 0 et " + str(len(handler.publication)-1)
		res = {'type': 'error', 'data': data}
		
	return json.dumps(res)
		
@route('/publications')
def publications2():
		res = handler.publication # récupère toutes les publications
		start = 0 # indice de départ par défaut à 0
		count = 100 # indice du nombre d'élément qu'on lit dans poublication par défaut à 100
		isOrder = False # si le parametre order est présent dans la route
		fields = ""
		fields2 = []
		isFields = False # si le parametre fields est présent dans la route
		errorData = ''
		
		# récupère le parametre start spécifié dans la route et vérifie s'il est inférieur à la taille de la liste publication
		try:
			if request.query['start'] != '' and int(request.query['start']) >= 0 and int(request.query['start']) < len(handler.publication):
				start = int(request.query['start'])
			else :
				errorData += 'Start '
		except KeyError:
			print("KeyError")
		
		# récupère le parametre count spécifié dans la route 
		try:
			if request.query['count'] != '':
				count = int(request.query['count'])
			else :
				errorData += 'Count '
		except KeyError:
			print("KeyError")
			
		try:
			if request.query['order'] != '': # récupère le parametre order 
				order = str(request.query['order'])
				isValid = False
				
				for champs in handler.champs: # vérifie si order est valide par rapport au clé du dictionnaire publication. 
					if order.lower().count(champs.lower()) > 0:
						isValid = True
						order = champs
						break
				
				if isValid:
					for i in range(0, len(res)): # tri par sélection des publications selon order
						min = res[i][order]
						
						for j in range(i+1, len(res)):
							if min[0].lower() > res[j][order][0].lower():
								res[i][order] = res[j][order]
								res[j][order] = min
								min = res[i][order]
								
					isOrder = True
			else : # si parametre order est vide
				errorData += 'Order '
						
		except KeyError:
			print("KeyError")
		
		try:
			if request.query['fields'] != '': # récupère le parametre fields spécifié dans la route
				fields = str(request.query['fields']).split(",") # met tous les champs dans une liste
			
				# vérifie si les champs sont valide et met les champs valide dans la variable field2
				for i in fields:
					for j in handler.champs:
						if i.lower().count(j.lower()) and len(i) == len(j):
							fields2.append(j)
				
				isFields = True
			
			else : # si parametre order est vide
				errorData += 'fields '
		except KeyError:
			print("KeyError")
		
		if (not(isOrder) or isOrder) and errorData == '': # si pas d'erreur 
			if not(isFields):
				return json.dumps({'type': 'ok', 'data': res[start:start+count]})
			elif isFields and len(fields2) > 0 :
				res2 = [] # liste contenant les champs spécifié
				for i in range(0, count): # récupère seulement les champs spécifié pour chaque publication
					d = {}
					if (start+i) < len(res): # si on ne dépasse pas le tableau
						for j in fields2: # pour chaque champs dans field2, on récupère seulement le champ
							d[j] = res[start+i][j]
						res2.append(d)
					else :
						break
				return json.dumps({'type': 'ok', 'data': res2})
			else :
				res = {'type': 'error', 'data': 'le champ specifie est incorrecte'}
				return json.dumps(res)
		else :
			return json.dumps({'type': 'error', 'data': 'parametre non defini : ' + errorData.replace(' ', '|')})

@route('/authors/<name>')
def authors(name):
		nbP = 0
		nbC = 0
		resFields = ["Nombre de Publication", "Nombre de Co auteur"] # clés du dictionnaire data
		fields = ""
		fields2 = []
		isFields = False # si le parametre fields est présent dans la route
		res2 = {}
		errorData = ''
		
		# pour chaque auteur dans chaque publication, on recherche l'auteur name
		for i in range(0, len(handler.publication)):
			for j in handler.publication[i]["author"]:
				if j.lower().count(name.lower()) > 0 and len(j) == len(name): # si auteur name trouve
					nbC = nbC + len(handler.publication[i]["author"]) - 1 # nombre de coauteur égale taille liste author - lui-meme + nbC
					nbP = nbP + 1 # incrémente le nombre de publication
		
		try:
			if request.query['fields'] != '': # on récupère le parametre fields et vérifions s'il est valide. Si c'est le cas, alors on ajoute dans la variable res2 la clé resFields[j] et comme valeur nbC ou nbP selon les cas
				fields = str(request.query['fields']).split(",")
			
				for i in fields:
					for j in range(0, len(resFields)):
						#if i.lower().count(resFields[j].lower()) and len(i) == len(resFields[j]):
						if i.lower() == resFields[j].lower():
							fields2.append(resFields[j])
							if j == 0:
								res2[resFields[0]] = nbP
							else :
								if j == 1:
									res2[resFields[1]] = nbC
				
				isFields = True
					
			else :
				errorData += 'fields '
		except KeyError:
			print("KeyError")
		
		if errorData == '':
			if not(isFields): # si pas d'erreur et pas de parametre fields dans la route
				res = {'type': 'ok', 'data': {resFields[0]: nbP, resFields[1]: nbC}}
			elif isFields and len(fields2) > 0: # si fields et champs valide supérieur à 0
				res = {'type': 'ok', 'data': res2}
			else : # erreur sur les valeurs de fields
				res = {'type': 'error', 'data': 'le champ specifie est incorrecte'}
		else :
			res = {'type': 'error', 'data': 'parametre non defini : ' + errorData}
			
		return json.dumps(res)
		
@route('/authors/<name>/publications')
def authorsP(name):
		res = []
		start = 0
		count = 100
		isOrder = False # si le parametre order est présent dans la route
		fields = ""
		fields2 = []
		isFields = False # si le parametre fields est présent dans la route
		errorData = ''
		
		# on récupère les publications de l'auteur ou coauteur name 
		for i in range(0, len(handler.publication)):
			for j in handler.publication[i]["author"]:
				if j.lower().count(name.lower()) > 0 and len(j) == len(name):
					res.append(handler.publication[i])
					break
		
		# récupère le parametre start spécifié dans la route et vérifie s'il est inférieur à la taille de la liste publication
		try:
			if request.query['start'] != '' and int(request.query['start']) < len(handler.publication):
				start = int(request.query['start'])
			else :
				errorData += 'Start '
		except KeyError:
			print("KeyError")
			
		try:
			if request.query['count'] != '':
				count = int(request.query['count'])
			else :
				errorData += 'Count '
		except KeyError:
			print("KeyError")
			
		try:
			if request.query['order'] != '':
				order = str(request.query['order'])
				isValid = False
				
				for champs in handler.champs:
					if order.lower().count(champs.lower()) > 0:
						isValid = True
						order = champs
						break
				
				if isValid:
					for i in range(0, len(res)):
						min = res[i][order]
						
						for j in range(i+1, len(res)):
							if min[0].lower() > res[j][order][0].lower():
								res[i][order] = res[j][order]
								res[j][order] = min
								min = res[i][order]
					isOrder = True
			else :
				errorData += 'Order '
						
		except KeyError:
			print("KeyError")
		
		try:
			if request.query['fields'] != '':
				fields = str(request.query['fields']).split(",")
			
				for i in fields:
					for j in handler.champs:
						if i.lower().count(j.lower()) and len(i) == len(j):
							fields2.append(j)
				
				isFields = True
					
			else :
				errorData += 'fields '
		except KeyError:
			print("KeyError")
		
		if (not(isOrder) or isOrder) and errorData == '':
			if not isFields:
				return json.dumps({'type': 'ok', 'data': res[start:start+count]})
			elif isFields and len(fields2) > 0:
				res2 = []
				for i in range(0, count):
					d = {}
					if (start+i) < len(res):
						for j in fields2:
							d[j] = res[start+i][j]
						res2.append(d)
					else :
						break
				return json.dumps({'type': 'ok', 'data': res2})
			else :
				res = {'type': 'error', 'data': 'le champ specifie est incorrecte'}
				return json.dumps(res)
		else :
			return json.dumps({'type': 'error', 'data': 'parametre non defini : ' + errorData.replace(' ', '|')})
		
@route('/authors/<name>/coauthors')
def coauthors(name):
		res = []
		isFind = False
		start = 0
		count = 100
		errorData = ''
						
		for i in range(0, len(handler.publication)):
			for j in handler.publication[i]["author"]:
				if j.lower().count(name.lower()) > 0:
					isFind = True
					break
			if isFind:
				for n in handler.publication[i]["author"]:
					if n.lower() != name.lower() and res.count(n) == 0:
						res.append(n)
				isFind = False
		
		# récupère le parametre start spécifié dans la route et vérifie s'il est inférieur à la taille de la liste publication
		try:
			if request.query['start'] != '' and int(request.query['start']) < len(handler.publication):
				start = int(request.query['start'])
			else :
				errorData += 'Start '
		except KeyError:
			print("KeyError")
			
		try:
			if request.query['count'] != '':
				count = int(request.query['count'])
			else :
				errorData += 'Count '
		except KeyError:
			print("KeyError")
		
		if errorData == '':
			return json.dumps({'type': 'ok', 'data': res[start:start+count]})
		else :
			return json.dumps({'type': 'error', 'data': 'parametre non defini : ' + errorData.replace(' ', '|')})

@route('/search/authors/<searchString>')
def searchA(searchString):
		res = []
		start = 0
		count = 100
		errorData = ''
		
		searchString = '^' + searchString
		if '%' in searchString:
			searchString = searchString.replace('%', '.?')

		if '*' in searchString:
			searchString = searchString.replace('*', '.*')
			
		for i in range(0, len(handler.publication)):
			for a in handler.publication[i]["author"]:
				search = re.search(searchString, a, re.I)
				
				if search and len(search.group()) == len(a) and res.count(a) == 0:
					print(search.group())
					res.append(a)
		
		# récupère le parametre start spécifié dans la route et vérifie s'il est inférieur à la taille de la liste publication
		try:
			if request.query['start'] != '' and int(request.query['start']) < len(handler.publication):
				start = int(request.query['start'])
			else :
				errorData += 'Start '
		except KeyError:
			print("KeyError")
			
		try:
			if request.query['count'] != '':
				count = int(request.query['count'])
			else :
				errorData += 'Count '
		except KeyError:
			print("KeyError")
			
		if errorData == '':
			return json.dumps({'type': 'ok', 'data': res[start:start+count]})
		else :
			return json.dumps({'type': 'error', 'data': 'parametre non defini : ' + errorData.replace(' ', '|')})
		
@route('/search/publications/<searchString>')
def searchP(searchString):
		res = []
		res2 = []
		isF = False
		start = 0
		count = 100
		isOrder = False # si le parametre order est présent dans la route
		fields = ""
		fields2 = []
		isFields = False # si le parametre fields est présent dans la route
		errorData = ''
		
		searchString = '^' + searchString
		if '%' in searchString:
			searchString = searchString.replace('%', '.?')

		if '*' in searchString:
			searchString = searchString.replace('*', '.*')
			
		for i in range(0, len(handler.publication)):
			for p in handler.publication[i]["title"]:
				search = re.search(searchString, p, re.I)
				
				if search and len(search.group()) == len(p):
					isF = True
					break
			if isF:
				res.append(handler.publication[i])
				isF = False
			
		try:
			query = request.query['filter']
			query = query.split(',')
			for q in query:
				q2 = q.split(':')
				for i in range(0, len(res)):
					for j in res[i][q2[0]]:
						print(q2[1], " ", j, " ", q2[1] in j)
						if q2[1] in j and res2.count(res[i]) == 0:
							res2.append(res[i])
				res = res2
				res2 = []
		except KeyError:
			print("KeyError")
		
		# récupère le parametre start spécifié dans la route et vérifie s'il est inférieur à la taille de la liste publication
		try:
			if request.query['start'] != '' and int(request.query['start']) < len(handler.publication):
				start = int(request.query['start'])
			else :
				errorData += 'Start '
		except KeyError:
			print("KeyError")
			
		try:
			if request.query['count'] != '':
				count = int(request.query['count'])
			else :
				errorData += 'Count '
		except KeyError:
			print("KeyError")
		
		try:
			if request.query['order'] != '':
				order = str(request.query['order'])
				isValid = False
				
				for champs in handler.champs:
					if order.lower().count(champs.lower()) > 0:
						isValid = True
						order = champs
						break
				
				if isValid:
					for i in range(0, len(res)):
						min = res[i][order]
						
						for j in range(i+1, len(res)):
							if min[0].lower() > res[j][order][0].lower():
								res[i][order] = res[j][order]
								res[j][order] = min
								min = res[i][order]
					isOrder = True
			else :
				errorData += 'Order '
						
		except KeyError:
			print("KeyError")
		
		try:
			if request.query['fields'] != '':
				fields = str(request.query['fields']).split(",")
			
				for i in fields:
					for j in handler.champs:
						if i.lower().count(j.lower()) and len(i) == len(j):
							fields2.append(j)
				
				isFields = True
					
			else :
				errorData += 'fields '
		except KeyError:
			print("KeyError")
				
		if (not(isOrder) or isOrder) and errorData == '':
			if not isFields:
				return json.dumps({'type': 'ok', 'data': res[start:start+count]})
			elif isFields and len(fields2) > 0:
				res2 = []
				for i in range(0, count):
					d = {}
					if (start+i) < len(res):
						for j in fields2:
							d[j] = res[start+i][j]
						res2.append(d)
					else :
						break
				return json.dumps({'type': 'ok', 'data': res2})
			else :
				res = {'type': 'error', 'data': 'le champ specifie est incorrecte'}
				return json.dumps(res)
		else :
			return json.dumps({'type': 'error', 'data': 'parametre non defini : ' + errorData.replace(' ', '|')})

def coauthors2(name):
	res = []
	isFind = False
	
	for i in range(0, len(handler.publication)):
			for j in handler.publication[i]["author"]: # trouve les coauteur de name
				if j.lower().count(name.lower()) > 0:
					isFind = True
					break
			if isFind:
				for n in handler.publication[i]["author"]: # récupère les coauteurs sans doublons
					if n.lower() != name.lower() and res.count(n) == 0:
						res.append(n)
				isFind = False
	return res
	
@route('/authors/<name_origine>/distance/<name_destination>')
def distance(name_origine, name_destination):
	res = []
	coauthor = []
	nonParcouru = {}
	chemin = []
	R = []
	
	if name_origine != name_destination: # si différent
		coauthor = coauthors2(name_origine) # liste de coauteur
		#print("coauthor> " + str(coauthor))
		
		# initialise dictionnaire nonParcouru à True
		for i in handler.publication:
			for j in i["author"]:
				if list(nonParcouru.keys()).count(j) == 0: # si j n'existe pas en tant que clé du dictionnaire alors on l'ajoute
					nonParcouru[j] = True
		
		chemin.append(name_origine) # ajoute name_origine dans la liste chemin
		while coauthor: # tant que la liste des coauteurs n'est pas vide, on fait un parcours en profondeur du graphe publication
			isFind = False
			u = coauthor[-1] # récupère le dernier élément de coauthor
			#print("u> " + u)
			for i in handler.publication: # récupère tous les coauteurs de u et les mets dans R
				R2 = []
				for j in i["author"]:
					if R.count(j) == 0 and nonParcouru[j]:
						R2.append(j)
						
						if j == u:
							isFind = True
					
				if isFind:
					for k in R2:
						if k != u and k != name_origine and coauthor.count(k) == 0: # ne récupère pas u lui-meme, name_origine et qu'il ne soit pas dans coauthor
							R.append(k)
					isFind = False
					#print("RR> " + str(R))
			
			#print("R> " + str(R))
			
			# on parcours tous les éléments de R
			# si R n'est pas vide, on retire le 1er élément de R et le met dans v. Ensuite, nous le notons comme étant parcouru (nonParcouru[v]) et ajoutons u dans chemin car nous l'avons déjà parcouru.
			# Enfin, nous ajoutons v dans coauthor afin de parcourir ses coauteurs.
			if R :
				v = R.pop(0)
				nonParcouru[v] = False
				chemin.append(u)
				coauthor.append(v)
				#print("nonParcouru[" + v + "]> " + str(nonParcouru[v]))
			else : # si r est vide, alors on supprime le dernier élément de coauthor. Puis, nous marquons u comme étant parcouru (nonParcouru[u]). Enfin, nous testons si u est égale à name_destination
				coauthor.pop()
				nonParcouru[u] = False
				#print("nonParcouru["+ u +"]> " + str(nonParcouru[u]))
				
				if u == name_destination and chemin.count(u) == 0:
					chemin.append(u)
					break
				
			#print("coauthor> " + str(coauthor))
			#print("chemin> " + str(chemin))
		
		# si dernier élément de chemin est égale à name_destination
		if chemin[-1] == name_destination:
			return json.dumps({"type": "ok", "data": {"chemin": chemin, "distance": len(chemin)-1}})
					
	return json.dumps({"type": "error", "data": "les auteurs n'ont jamais travailler indirectement"})
		
run(host='localhost', port=8080, debug = True)
