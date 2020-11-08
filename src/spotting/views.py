import re
import sys
import json as JSON
import time as TIME
# from operator import itemgetter

# sys.path.append("..")
from trains.models import Train

from django.conf import settings as glob
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

def AwardThisUser(Username, award):
	userInfoRef = glob.COUCH_USER_INFO[ PARTITION_KEY_DICT[ Username[0].lower() ] + ':' + Username ]
	if 'Achievements' in dict(userInfoRef).keys() and len(userInfoRef['Achievements']):
		userInfoRef['Achievements'].append(award)
	else:
		userInfoRef['Achievements'] = [str(award)]
	userInfoRef.save()
	print("[AWARD] New achievement by {}: {}".format(Username, award))

def CreateUserActivity(Username):
	newDoc = {}
	newDoc['_id'] = PARTITION_KEY_DICT[ Username[0].lower() ] + ':' + Username
	newDoc['key'] = PARTITION_KEY_DICT[ Username[0].lower() ] + ':' + Username
	glob.COUCH_USER_ACTIVITY.create_document(newDoc)

def FirstSpottingByUser(userRef, spottingDoc):
	del spottingDoc['Username']
	userRef[ 'Spottings' ] = [spottingDoc]
	userRef.save()
	''' Your First Spotting '''
	AwardThisUser(Username, "YFS")

def AnotherSpottingByUser(userRef, spottingDoc):
	del spottingDoc['Username']
	userRef[ 'Spottings' ].append(spottingDoc)
	userRef.save()

def FirstSpottingOfLoco(spottingDoc):
	newDoc = dict(_id = str(spottingDoc[ 'Loco_Number' ]), key = str(spottingDoc[ 'Loco_Number' ]))
	del spottingDoc['Loco_Number']
	newDoc[ 'Spottings' ] = [spottingDoc]
	glob.COUCH_OVERALL_SPOTTING.create_document(newDoc)
	''' First To Spot Loco '''
	AwardThisUser(spottingDoc['Username'], "FTSL")

def AnotherSpottingOfLoco(overallRef, spottingDoc):
	del spottingDoc['Loco_Number']
	overallRef[ 'Spottings' ].append(spottingDoc)
	overallRef.save()

@csrf_exempt
def NewSpottingHandler(req):
	if not req.body:
		glob.LOGGER("[NEW SPOT] Invalid Request: Null body")
		print("[NEW SPOT] Invalid Request: Null body")
		return HttpResponse(status = 400)
	body = JSON.loads(req.body)
	if 'Whos_Asking' not in body or not body['Whos_Asking']:
		glob.LOGGER("[NEW SPOT] Invalid Request: Null Whos_Asking")
		print("[NEW SPOT] Invalid Request: Null Whos_Asking")
		return HttpResponse(status = 400)

	Username = body['Whos_Asking']

	glob.LOGGER("[NEW SPOT] Request by {}: \n {}".format(Username, str(body)))
	print("[NEW SPOT] Request by {}: \n {}".format(Username, str(body)))
	
	spottingDoc = { k:v for k,v in body.items() if v }
	spottingDoc[ 'Spotting_ID' ] = Username + ':' + glob.RAND6DIG()
	spottingDoc[ 'Loco_Number' ] = "Uncertain" if 'Loco_Number' not in body else int(body['Loco_Number'])
	spottingDoc[ 'Date_Time' ] = int(body['Date_Time']) if 'Date_Time' in body else int(TIME.time())

	try:
		selector = { "Spottings": { "$elemMatch": { "Loco_Class": spottingDoc[ 'Loco_Class' ] } } }
		classRef = list(glob.COUCH_OVERALL_SPOTTING.get_query_result(selector))
		if len(classRef) < 1:
			''' First To Spot Loco Class '''
			glob.LOGGER("[NEW SPOT] First spotting of Class: {}".format(spottingDoc[ 'Loco_Class' ]))
			print("[NEW SPOT] First spotting of Class: {}".format(spottingDoc[ 'Loco_Class' ]))
			AwardThisUser(Username, "FTSLC")
	except Exception as e:
		glob.LOGGER("[NEW SPOT] Exception @ Loco_Class \n {}".format(e))
		print("[NEW SPOT] Exception @ Loco_Class \n {}".format(e))

	try:
		selector = { "Spottings": { "$elemMatch": { "Loco_Shed": spottingDoc[ 'Loco_Shed' ] } } }
		shedRef = list(glob.COUCH_OVERALL_SPOTTING.get_query_result(selector))
		if len(shedRef) < 1:
			''' First To Spot Loco Shed '''
			glob.LOGGER("[NEW SPOT] First spotting of Shed: {}".format(spottingDoc[ 'Loco_Shed' ]))
			print("[NEW SPOT] First spotting of Shed: {}".format(spottingDoc[ 'Loco_Shed' ]))
			AwardThisUser(Username, "FTSLS")
	except Exception as e:
		glob.LOGGER("[NEW SPOT] Exception @ Loco_Shed \n {}".format(e))
		print("[NEW SPOT] Exception @ Loco_Shed \n {}".format(e))

	try:
		selector = { "Spottings": { "$elemMatch": { "Train_Number": spottingDoc[ 'Train_Number' ] } } }
		trainRef = list(glob.COUCH_OVERALL_SPOTTING.get_query_result(selector))
		if len(trainRef) < 1:
			''' First To Spot Train '''
			glob.LOGGER("[NEW SPOT] First spotting of Train: {}".format(spottingDoc[ 'Train_Number' ]))
			print("[NEW SPOT] First spotting of Train: {}".format(spottingDoc[ 'Train_Number' ]))
			AwardThisUser(Username, "FTST")
	except Exception as e:
		glob.LOGGER("[NEW SPOT] Exception @ Train_Number \n {}".format(e))
		print("[NEW SPOT] Exception @ Train_Number \n {}".format(e))
		
	try:
		overallRef = glob.COUCH_OVERALL_SPOTTING[ str(spottingDoc[ 'Loco_Number' ]) ]
		glob.LOGGER("[NEW SPOT] Spotting of Loco {} already exists".format(spottingDoc[ 'Loco_Number' ]))
		print("[NEW SPOT] Spotting of Loco {} already exists".format(spottingDoc[ 'Loco_Number' ]))
		AnotherSpottingOfLoco(overallRef, { **spottingDoc })
	except KeyError:
		glob.LOGGER("[NEW SPOT] First spotting of Loco: {}".format(spottingDoc[ 'Loco_Number' ]))
		print("[NEW SPOT] First spotting of Loco: {}".format(spottingDoc[ 'Loco_Number' ]))
		FirstSpottingOfLoco({ **spottingDoc })
	except Exception as err:
		glob.LOGGER("[NEW SPOT] Error @ Overall Ref \n {}".format(err))
		print("[NEW SPOT] Error @ Overall Ref \n {}".format(err))
		return HttpResponse(status = 500)

	try:
		userRef = glob.COUCH_USER_ACTIVITY[ PARTITION_KEY_DICT[ Username[0].lower() ] + ':' + Username ]
		glob.LOGGER("[NEW SPOT] {} has previous activity".format(Username))
		print("[NEW SPOT] {} has previous activity".format(Username))
	except KeyError:
		glob.LOGGER("[NEW SPOT] First activity by user {}".format(Username))
		print("[NEW SPOT] First activity by user {}".format(Username))
		CreateUserActivity(Username)
		userRef = glob.COUCH_USER_ACTIVITY[ PARTITION_KEY_DICT[ Username[0].lower() ] + ':' + Username ]
	except Exception as err:
		glob.LOGGER("[NEW SPOT] Error @ User Ref \n {}".format(err))
		print("[NEW SPOT] Error @ User Ref \n {}".format(err))
		return HttpResponse(status = 500)

	try:
		glob.COUCH_USER_ACTIVITY[ PARTITION_KEY_DICT[ Username[0].lower() ] + ':' + Username ]['Spottings']
		glob.LOGGER("[NEW SPOT] {} has previous spottings".format(Username))
		print("[NEW SPOT] {} has previous spottings".format(Username))
		AnotherSpottingByUser(userRef, { **spottingDoc })
		glob.LOGGER("[NEW SPOT] {} added spotting {}".format(Username, str(spottingDoc)))
		print("[NEW SPOT] {} added spotting {}".format(Username, str(spottingDoc)))
	except KeyError:
		glob.LOGGER("[NEW SPOT] First spotting by {}".format(Username))
		print("[NEW SPOT] First spotting by {}".format(Username))
		FirstSpottingByUser(userRef, { **spottingDoc })
		glob.LOGGER("[NEW SPOT] {} added spotting {}".format(Username, str(spottingDoc)))
		print("[NEW SPOT] {} added spotting {}".format(Username, str(spottingDoc)))
	except Exception as err:
		glob.LOGGER("[NEW SPOT] Error @ User Ref \n {}".format(err))
		print("[NEW SPOT] Error @ User Ref \n {}".format(err))
		return HttpResponse(status = 500)

	glob.LOGGER("[NEW SPOT] Request handled successfully! Response: 201")
	print("[NEW SPOT] Request handled successfully! Response: 201")
	return HttpResponse(status = 201)

@csrf_exempt
def UserSpottingHandler(req):
	if not req.body:
		glob.LOGGER("[USER SPOT] Invalid Request: Null body")
		print("[USER SPOT] Invalid Request: Null body")
		return HttpResponse(status = 400)
	body = JSON.loads(req.body)
	if 'Whos_Asking' not in body or not body['Whos_Asking']:
		glob.LOGGER("[USER SPOT] Invalid Request: Null Whos_Asking")
		print("[USER SPOT] Invalid Request: Null Whos_Asking")
		return HttpResponse(status = 400)
	
	Username = body[ 'Whos_Asking' ] if 'Username' not in body else body[ 'Username' ]
	if body[ 'Username' ]:
		print("[USER SPOT] Request for {} by {}".format(Username, body[ 'Whos_Asking' ]))
	else:
		print("[USER SPOT] Request by {}".format(Username))
	
	try:
		spottingList = glob.COUCH_USER_ACTIVITY[\
			PARTITION_KEY_DICT[ Username[0].lower() ] + ':' + Username\
		][ 'Spottings' ]

		for sDoc in spottingList:
			if 'Train_Number' in sDoc:
				try:
					trainQuery = list(\
						Train.objects.filter(\
							Train_Number = int(sDoc[ 'Train_Number' ])\
						).values_list('Train_Name', flat=True)\
					)
					sDoc.update({ "Train_Name": trainQuery[0] })
				except:
					print("[USER SPOT] Could not find train {}".format(sDoc['Train_Number']))

		spottingList.sort(key = lambda doc: doc['Date_Time'], reverse = True)
		glob.LOGGER("[USER SPOT] Request handled successfully! Response: \n {}".format(str(spottingList)))
		print("[USER SPOT] Request handled successfully! Response: \n {}".format(str(spottingList)))
		return JsonResponse(spottingList, safe = False)
	except KeyError:
		print("[USER SPOT] No spottings found for {}".format(Username))
		print("[USER SPOT] Request handled successfully! Response: 404")
		return HttpResponse(status = 404)
	except Exception as err:
		print("[USER SPOT] Error: \n {}".format(err))
		return HttpResponse(status = 500)

@csrf_exempt
def ListSpottingHandler(req):
	# print(LOGGER)
	body = JSON.loads(req.body)
	print("[LIST SPOT] New request\n {}".format(body))
	glob.LOGGER("[LIST SPOT] New request\n {}".format(body))
	res = []

	''' Loco_Number '''
	if 'Loco_Number' in body.keys():
		print("[LIST SPOT] List for Loco {}".format(body['Loco_Number']))
		overallRef = list(glob.COUCH_OVERALL_SPOTTING[ str(body['Loco_Number']) ]['Spottings'])
		res.extend(overallRef)

	''' Shed Class '''
	if 'Loco_Class' in body.keys():
		print("[LIST SPOT] List for Class {}".format(body['Loco_Class']))
		selector = { "Spottings": { "$elemMatch": { "Loco_Class": body['Loco_Class'] } } }
		overallRef = list(glob.COUCH_OVERALL_SPOTTING.get_query_result(selector, fields = ["Spottings"]))
		res.extend([\
			spottingDoc for docs in overallRef for spottingDoc in docs['Spottings']\
			if spottingDoc['Loco_Class'] == body['Loco_Class']\
		])

	if 'Loco_Shed' in body.keys():
		print("[LIST SPOT] List for Shed {}".format(body['Loco_Shed']))
		selector = { "Spottings": { "$elemMatch": { "Loco_Shed": body['Loco_Shed'] } } }
		overallRef = list(glob.COUCH_OVERALL_SPOTTING.get_query_result(selector, fields = ["Spottings"]))
		res.extend([\
			spottingDoc for docs in overallRef for spottingDoc in docs['Spottings']\
			if spottingDoc['Loco_Shed'] == body['Loco_Shed']\
		])

	''' Train_Number '''
	if 'Train_Number' in body.keys():
		print("[LIST SPOT] List for Train {}".format(body['Train_Number']))
		selector = { "Spottings": { "$elemMatch": { "Train_Number": body['Train_Number'] } } }
		overallRef = list(glob.COUCH_OVERALL_SPOTTING.get_query_result(selector, fields = ["Spottings"]))
		res.extend([\
			spottingDoc for docs in overallRef for spottingDoc in docs['Spottings']\
			if spottingDoc['Train_Number'] == body['Train_Number']\
		])

	''' Train_Name '''
	if 'Train_Name' in body.keys():
		print("[LIST SPOT] List for Train Name {}".format(body['Train_Name']))
		trainNum = list(\
			glob.COUCH_TRAIN_DATA.get_query_result(\
				{ "Train_Name": { "$eq": body['Train_Name'] } }, fields = ['Train_Number']\
			)\
		)
		for num in trainNum:
			selector = 	{ "Spottings": { "$elemMatch": { "Train_Number": num['Train_Number'] } } }
			overallRef = list(glob.COUCH_OVERALL_SPOTTING.get_query_result(selector, fields = ["Spottings"]))
			res.extend([\
				spottingDoc for docs in overallRef for spottingDoc in docs['Spottings']\
				if spottingDoc['Train_Number'] == num['Train_Number']\
			])
	res.sort(key = lambda doc: doc['Date_Time'], reverse = True)
	return JsonResponse(res, safe = False)

@csrf_exempt
def EditSpottingHandler(req):
	body = JSON.loads(req.body)
	print("[EDIT SPOT] New request\n {}".format(body))
	
	if not 'Edits' in body.keys() or not body['Edits']:
		print("[EDIT SPOT] No edits mentioned!")
		return HttpResponse(status = 400)

	def editUserSpotting(Username, existingDoc, editsDoc):
		print("[EDIT SPOT] editUserSpotting")
		try:
			userRef = glob.COUCH_USER_ACTIVITY[ ':'.join((PARTITION_KEY_DICT[ Username[0].lower() ], Username)) ]
			withoutUser = { key:val for key, val in existingDoc.items() if key != 'Username' }	
			index = userRef['Spottings'].index(withoutUser)
			userRef['Spottings'][ index ].update(editsDoc)
			userRef.save()
		except ValueError as ve:
			print("[EDIT SPOT] Could not find doc in existing list")
		except Exception as err:
			print("[EDIT SPOT] editUserSpotting error: \n {}".format(err))
			return HttpResponse(status = 500)

	def editOverallSpotting(existingDoc, editsDoc):
		print("[EDIT SPOT] editOverallSpotting")
		if 'Loco_Number' in editsDoc.keys():
			try:
				overallRef = glob.COUCH_OVERALL_SPOTTING[ str(existingDoc['Loco_Number']) ]
				withoutLoco = { key:val for key, val in existingDoc.items() if key != 'Loco_Number' }
				# withoutLoco = { key:existingDoc[key] for key in existingDoc.keys() if key != 'Loco_Number' }
				index = overallRef['Spottings'].index(withoutLoco)
				del overallRef['Spottings'][index]
				''' Deleting Old '''
				if len(overallRef['Spottings']) == 0:
					overallRef.delete()
				overallRef.save()
			except ValueError as ve:
				print("[EDIT SPOT] Could not find doc in existing list")
			except Exception as e:
				print("[EDIT SPOT] Exception at deleting existing doc \n {}".format(e))
			
			existingDoc.update(editsDoc)
			
			try:
				''' Check Existing '''
				newOverallRef = glob.COUCH_OVERALL_SPOTTING[ str(editsDoc['Loco_Number']) ]
				AnotherSpottingOfLoco(newOverallRef, existingDoc)
			except KeyError:
				''' Create New '''
				print("[EDIT SPOT] First spotting of loco: {}".format(editsDoc['Loco_Number']))
				FirstSpottingOfLoco(existingDoc)
			except Exception as err:
				print("[EDIT SPOT] editOverallSpotting error: \n {}".format(err))
		else:
			overallRef = glob.COUCH_OVERALL_SPOTTING[ str(existingDoc['Loco_Number']) ]
			withoutLoco = { key:existingDoc[key] for key in existingDoc.keys() if key != 'Loco_Number' }
			overallRef['Spottings'][ overallRef['Spottings'].index(withoutLoco) ].update(editsDoc)

	editUserSpotting(body['Username'], body['Existing_Doc'], body['Edits'])
	editOverallSpotting(body['Existing_Doc'], body['Edits'])

	return HttpResponse(status = 200)

@csrf_exempt
def SearchSpottingHandler(req):
	body = JSON.loads(req.body)
	searchTerm = body['Search_Term']

	print("[SEARCH SPOT] Term to search: {}".format(searchTerm))

	tlNumRegx = r"^\d{3,5}$";
	tNameRegx = r"\w{5,}"
	lClassRegx = r"[A-Z0-9]{3,5}"
	lShedRegx = r"[A-Z0-9]{3,5}"
	shedClassRegx = r"[A-Z0-9]{3,5}\s[A-Z0-9]{3,5}"
	
	res = []
	if re.match(tlNumRegx, str(searchTerm)):
		''' Search Loco Number '''
		try:
			overallRef = glob.COUCH_OVERALL_SPOTTING[ str(searchTerm) ]
			for spottingDoc in overallRef['Spottings']:
				spottingDoc['Loco_Number'] = overallRef['Loco_Number']
				if 'Train_Number' in spottingDoc and 'Train_Name' not in spottingDoc:
					try:
						trainRef = glob.COUCH_TRAIN_DATA[ str(spottingDoc[ 'Train_Number' ]) ]['Train_Name']
						spottingDoc['Train_Name'] = trainRef
					except Exception as e:
						print("[SEARCH SPOT] Could not find Train Name of {}".format(spottingDoc[ 'Train_Number' ]))
				res.append(spottingDoc)
		except KeyError:
			print("[SEARCH SPOT] Could not find {} loco number".format(searchTerm))
		except Exception as err:
			print("[SEARCH SPOT] Error @ loco number \n {}".format(err))
		''' Search Train Number '''
		try:
			selector = { "Spottings": { "$elemMatch": { "Train_Number": int(searchTerm) } } }
			overallRef = list(glob.COUCH_OVERALL_SPOTTING.get_query_result(selector, fields = ['Loco_Number', 'Spottings']))
			for docs in overallRef:
				for spottingDoc in docs['Spottings']:
					if 'Train_Number' in spottingDoc and spottingDoc['Train_Number'] == int(searchTerm):
						spottingDoc['Loco_Number'] = docs['Loco_Number']
						if 'Train_Number' in spottingDoc and 'Train_Name' not in spottingDoc:
							try:
								trainRef = glob.COUCH_TRAIN_DATA[ str(spottingDoc[ 'Train_Number' ]) ]['Train_Name']
								spottingDoc['Train_Name'] = trainRef
							except Exception as e:
								print("[SEARCH SPOT] Could not find Train Name of {}".format(spottingDoc[ 'Train_Number' ]))
						res.append(spottingDoc)
		except KeyError:
			print("[SEARCH SPOT] Could not find {} train number".format(searchTerm))
		except Exception as err:
			print("[SEARCH SPOT] Error @ train number \n {}".format(err))

	if re.match(tNameRegx, searchTerm):
		''' Search Train Name '''
		# try:
		# 	selector = { "Spottings": { "$elemMatch": { "Train_Number": { "$exists": True } } } }
		# 	overallRef = list(glob.COUCH_OVERALL_SPOTTING.get_query_result(selector, fields = ['Loco_Number', 'Spottings']))
		# 	# res.extend(spottingDoc for doc in trainRef for spottingDoc in doc['Spottings'])
		# 	for docs in overallRef:
		# 		if 'Loco_Number' and 'Spottings' in docs:
		# 			print(JSON.dumps(docs['Spottings'], indent=4))
		# except Exception as err:
		# 	print(err)
	if re.match(lClassRegx, searchTerm):
		''' Search Loco Class '''
		selector = { "Spottings": { "$elemMatch": { "Loco_Class": searchTerm } } }
		overallRef = list(glob.COUCH_OVERALL_SPOTTING.get_query_result(selector, fields = ["Loco_Number", "Spottings"]))
		for docs in overallRef:
			for spottingDoc in docs['Spottings']:
				if 'Loco_Class' in spottingDoc and spottingDoc['Loco_Class'] == searchTerm:
					spottingDoc['Loco_Number'] = docs['Loco_Number']
					if 'Train_Number' in spottingDoc and 'Train_Name' not in spottingDoc:
						try:
							trainRef = glob.COUCH_TRAIN_DATA[ str(spottingDoc[ 'Train_Number' ]) ]['Train_Name']
							spottingDoc['Train_Name'] = trainRef
						except Exception as e:
							print("[SEARCH SPOT] Could not find Train Name of {}".format(spottingDoc[ 'Train_Number' ]))
					res.append(spottingDoc)

	if re.match(lShedRegx, searchTerm):
		''' Search Loco Shed '''
		selector = { "Spottings": { "$elemMatch": { "Loco_Shed": searchTerm } } }
		overallRef = list(glob.COUCH_OVERALL_SPOTTING.get_query_result(selector, fields = ["Loco_Number", "Spottings"]))
		for docs in overallRef:
			for spottingDoc in docs['Spottings']:
				if 'Loco_Shed' in spottingDoc and spottingDoc['Loco_Shed'] == searchTerm:
					spottingDoc['Loco_Number'] = docs['Loco_Number']
					if 'Train_Number' in spottingDoc and 'Train_Name' not in spottingDoc:
						try:
							trainRef = glob.COUCH_TRAIN_DATA[ str(spottingDoc[ 'Train_Number' ]) ]['Train_Name']
							spottingDoc['Train_Name'] = trainRef
						except Exception as e:
							print("[SEARCH SPOT] Could not find Train Name of {}".format(spottingDoc[ 'Train_Number' ]))
					res.append(spottingDoc)

	if re.match(shedClassRegx, searchTerm.upper()):
		''' Search Shed-Class '''
		print("MATCHES SHED CLASS")
		overallRef = list(glob.COUCH_OVERALL_SPOTTING)
		# print(overallRef)
		for docs in overallRef:
			for spottingDoc in docs['Spottings']:
				if 'Loco_Class' in spottingDoc and re.match(spottingDoc['Loco_Class'], searchTerm.upper())\
				or 'Loco_Shed' in spottingDoc and re.match(spottingDoc['Loco_Shed'], searchTerm.upper()):
					if 'Train_Number' in spottingDoc and 'Train_Name' not in spottingDoc:
						try:
							trainRef = glob.COUCH_TRAIN_DATA[ str(spottingDoc[ 'Train_Number' ]) ]['Train_Name']
							spottingDoc['Train_Name'] = trainRef
						except Exception as e:
							print("[SEARCH SPOT] Could not find Train Name of {}".format(spottingDoc[ 'Train_Number' ]))
					res.append(spottingDoc)

	res.sort(key = lambda doc: doc['Date_Time'], reverse = True)
	return JsonResponse(res, safe = False)