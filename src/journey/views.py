import os
import re
import sys
import datetime as DT
import json as JSON
import time as TIME
from random import randint as RANDINT

sys.path.append("..")
from trains.models import Train

from django.conf import settings as glob
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

def AwardThisUser(Username, award):
	userInfoRef = glob.COUCH_USER_INFO[ ':'.join((glob.PARTITION_KEY_DICT[ Username[0].lower() ], Username)) ]
	if 'Achievements' in userInfoRef.keys() and len(userInfoRef['Achievements']):
		userInfoRef['Achievements'].append(award) if award not in userInfoRef['Achievements'] else None
	else:
		userInfoRef['Achievements'] = [award]
	userInfoRef.save()
	glob.LOGGER("[AWARD] New achievement by {}: {}".format(Username, award))
	print("[AWARD] New achievement by {}: {}".format(Username, award))

def CreateUserActivity(Username):
	newDoc = {}
	newDoc['_id'] = ':'.join((glob.PARTITION_KEY_DICT[ Username[0].lower() ], Username))
	newDoc['key'] = ':'.join((glob.PARTITION_KEY_DICT[ Username[0].lower() ], Username))
	glob.COUCH_USER_ACTIVITY.create_document(newDoc)

@csrf_exempt
def NewJourneyHandler(req):
	if not req.body:
		glob.LOGGER("[NEW JRNY] Invalid Request: Null body")
		print("[NEW JRNY] Invalid Request: Null body")
		return HttpResponse(status = 400)
	body = JSON.loads(req.body)
	if not 'Whos_Asking' in body.keys() or not body['Whos_Asking']:
		glob.LOGGER("[NEW JRNY] Invalid Request: Missing Whos_Asking")
		print("[NEW JRNY] Invalid Request: Missing Whos_Asking")
		return HttpResponse(status = 400)

	Username = body['Whos_Asking']

	glob.LOGGER("[NEW JRNY] New request by {}: \n {}".format(Username, str(body)))
	print("[NEW JRNY] New request by {}: \n {}".format(Username, str(body)))

	journeyDoc = { k:v for k,v in body.items() if v and k not in ('Username', 'Private') }
	journeyDoc['Date_Time'] = int(TIME.time())
	# journeyDoc['Journey_ID'] = ':'.join((Username, 'J'+str(RANDINT(1001, 9999))+str(RANDINT(1001, 9999))))
	# "".join([random.choice(string.ascii_letters) for i in range(20)])

	try:
		userRef = glob.COUCH_USER_ACTIVITY[ ':'.join((glob.PARTITION_KEY_DICT[ Username[0].lower() ], Username)) ]
		glob.LOGGER("[NEW JRNY] User {} has previous activity".format(Username))
		print("[NEW JRNY] User {} has previous activity".format(Username))
	except KeyError:
		glob.LOGGER("[NEW JRNY] First activity by user {}".format(Username))
		print("[NEW JRNY] First activity by user {}".format(Username))
		CreateUserActivity(Username)
		userRef = glob.COUCH_USER_ACTIVITY[ ':'.join((glob.PARTITION_KEY_DICT[ Username[0].lower() ], Username)) ]
	except Exception as err:
		glob.LOGGER("[NEW JRNY] Error at userRef \n {}".format(err))
		print("[NEW JRNY] Error at userRef \n {}".format(err))

	if 'Private' in body.keys() and bool(body['Private']):
		''' Private Journey '''
		if 'Private_Journeys' in userRef:
			''' Another Journey '''
			glob.LOGGER("[NEW JRNY] User {} has previous Private Journeys".format(Username))
			print("[NEW JRNY] User {} has previous Private Journeys".format(Username))
			userRef['Private_Journeys'].append(journeyDoc)
			userRef.save()
		else:
			''' First Journey '''
			glob.LOGGER("[NEW JRNY] First Private Journey of User {}".format(Username))
			print("[NEW JRNY] First Private Journey of User {}".format(Username))
			userRef['Private_Journeys'] = [journeyDoc]
			userRef.save()
			AwardThisUser(Username, "YFJ")
	else:
		''' Public Journey '''
		if 'Journeys' in userRef:
			''' Another Journey '''
			glob.LOGGER("[NEW JRNY] User {} has previous Journeys".format(Username))
			print("[NEW JRNY] User {} has previous Journeys".format(Username))
			userRef['Journeys'].append(journeyDoc)
			userRef.save()
		else:
			''' First Journey '''
			glob.LOGGER("[NEW JRNY] First Journey of User {}".format(Username))
			print("[NEW JRNY] First Journey of User {}".format(Username))
			userRef['Journeys'] = [journeyDoc]
			userRef.save()
			AwardThisUser(Username, "YFJ")

	glob.LOGGER("[NEW JRNY] Request handled successfully! Response: 200")
	print("[NEW JRNY] Request handled successfully! Response: 200")
	return HttpResponse(status = 200)

@csrf_exempt
def UserJourneysHandler(req):
	if not req.body:
		glob.LOGGER("[LIST JRNY] Invalid Request: Null body")
		print("[LIST JRNY] Invalid Request: Null body")
		return HttpResponse(status = 400)
	body = JSON.loads(req.body)
	if not 'Username' in body.keys() or not body['Username']:
		glob.LOGGER("[LIST JRNY] Invalid Request: Missing Username")
		print("[LIST JRNY] Invalid Request: Missing Username")
		return HttpResponse(status = 400)
	
	Username = body['Username']
	res = []

	if 'Whos_Asking' in body.keys() and body['Whos_Asking']:
		privileged = bool(body['Username'] == body['Whos_Asking'])
		glob.LOGGER("[LIST JRNY] Request by {} for {}: \n {}".format(body['Whos_Asking'], Username, str(body)))
		print("[LIST JRNY] Request by {} for {}: \n {}".format(body['Whos_Asking'], Username, str(body)))
	else:
		glob.LOGGER("[LIST JRNY] Request for {}: \n {}".format(Username, str(body)))
		print("[LIST JRNY] Request for {}: \n {}".format(Username, str(body)))

	try:
		userRef = glob.COUCH_USER_ACTIVITY[\
			':'.join((glob.PARTITION_KEY_DICT[ Username[0].lower() ], Username))\
		]['Journeys']
		glob.LOGGER("[LIST JRNY] User {} has previous journeys".format(Username))
		print("[LIST JRNY] User {} has previous journeys".format(Username))
		
		for jDoc in userRef:
			if 'Train_Number' in jDoc and 'Train_Name' not in jDoc:
				try:
					trainQuery = list(\
						Train.objects.filter(\
							Train_Number = int(jDoc[ 'Train_Number' ])\
						).values_list('Train_Name', flat=True)\
					)
					jDoc.update({ "Train_Name": trainQuery[0] })
				except:
					print("[LIST JRNY] Could not find train {}".format(jDoc['Train_Number']))
			res.append(jDoc)

		# for journeyDoc in userRef:
		# 	if 'Train_Number' in journeyDoc and 'Train_Name' not in journeyDoc:
		# 		trainRef = glob.COUCH_TRAIN_DATA[ str(journeyDoc[ 'Train_Number' ]) ]['Train_Name']
		# 		journeyDoc['Train_Name'] = trainRef
		# 	res.append(journeyDoc)


	except KeyError:
		glob.LOGGER("[LIST JRNY] User {} does not have journeys".format(Username))
		print("[LIST JRNY] User {} does not have journeys".format(Username))
	except Exception as err:
		glob.LOGGER("[LIST JRNY] Error: \n {}".format(err))
		print("[LIST JRNY] Error: \n {}".format(err))
		return HttpResponse(status = 500)
	
	if 'Private' in body.keys() and bool(body['Private']) and privileged:
		try:
			userRef = glob.COUCH_USER_ACTIVITY[\
				':'.join((glob.PARTITION_KEY_DICT[ Username[0].lower() ], Username))\
			]['Private_Journeys']
			glob.LOGGER("[LIST JRNY] User {} has previous Private Journeys".format(Username))
			print("[LIST JRNY] User {} has previous Private Journeys".format(Username))
			
			for jDoc in userRef:
				if 'Train_Number' in jDoc and 'Train_Name' not in jDoc:
					try:
						trainQuery = list(\
							Train.objects.filter(\
								Train_Number = int(jDoc[ 'Train_Number' ])\
							).values_list('Train_Name', flat=True)\
						)
						jDoc.update({ "Train_Name": trainQuery[0] })
					except:
						print("[LIST JRNY] Could not find train {}".format(jDoc['Train_Number']))
				res.append(jDoc)


			# for journeyDoc in userRef:
			# 	journeyDoc['Private'] = True
			# 	if 'Train_Number' in journeyDoc and 'Train_Name' not in journeyDoc:
			# 		trainRef = glob.COUCH_TRAIN_DATA[ str(journeyDoc[ 'Train_Number' ]) ]['Train_Name']
			# 		journeyDoc['Train_Name'] = trainRef
			# 	res.append(journeyDoc)


		except KeyError:
			glob.LOGGER("[LIST JRN] User {} does not have Private Journeys".format(Username))
			print("[LIST JRN] User {} does not have Private Journeys".format(Username))
		except Exception as err:
			glob.LOGGER("[LIST JRNY] Error: \n {}".format(err))
			print("[LIST JRNY] Error: \n {}".format(err))
			return HttpResponse(status = 500)

	if not len(res):
		glob.LOGGER("[LIST JRNY] Request handled successfully! Response: 204")
		print("[LIST JRNY] Request handled successfully! Response: 204")
		return JsonResponse([], safe = False, status = 204)
	else:
		res.sort(key = lambda doc: doc['Date_Time'], reverse = True)
		glob.LOGGER("[LIST JRNY] Request handled successfully! Response: \n {}".format(str(res)))
		print("[LIST JRNY] Request handled successfully! Response: \n {}".format(str(res)))
		return JsonResponse(res, safe = False)

@csrf_exempt
def TimeJourneysHandler(req):
	if not req.body:
		glob.LOGGER("[TIME JRNY] Invalid Request: Null body")
		print("[TIME JRNY] Invalid Request: Null body")
		return HttpResponse(status = 400)
	body = JSON.loads(req.body)
	if not 'Username' in body.keys() or not body['Username']:
		glob.LOGGER("[TIME JRNY] Invalid Request: Missing Username")
		print("[TIME JRNY] Invalid Request: Missing Username")
		return HttpResponse(status = 400)
	if not 'Search_Time' in body.keys() or not body['Search_Time']:
		glob.LOGGER("[TIME JRNY] Invalid Request: Missing Search Time")
		print("[TIME JRNY] Invalid Request: Missing Search Time")
		return HttpResponse(status = 400)
	if not 'Search_Type' in body.keys() or not body['Search_Type'] or body['Search_Type'] not in ('At', 'Over', 'Under'):
		glob.LOGGER("[TIME JRNY] Invalid Request: Missing Search Type")
		print("[TIME JRNY] Invalid Request: Missing Search Type")
		return HttpResponse(status = 400)

	Username = body['Username']
	searchTime = int(body['Search_Time'])

	if 'Whos_Asking' in body.keys() and body['Whos_Asking']:
		privileged = bool(body['Username'] == body['Whos_Asking'])
		glob.LOGGER("[TIME JRNY] Request by {} for {}: \n {}".format(body['Whos_Asking'], Username, body))
		print("[TIME JRNY] Request by {} for {}: \n {}".format(body['Whos_Asking'], Username, body))
	else:
		glob.LOGGER("[TIME JRNY] Request for {}: \n {}".format(Username, body))
		print("[TIME JRNY] Request for {}: \n {}".format(Username, body))

	def SeachTimeInJourneysArray(journeysArray, searchTime, searchType):
		if searchType == 'At':
			''' At / On '''
			glob.LOGGER("[TIME JRNY] At request")
			print("[TIME JRNY] At request")
			return list(filter(lambda journeyDoc:\
					'Time_In' in journeyDoc and 'Time_Out' in journeyDoc\
					and journeyDoc['Time_In'] < searchTime and journeyDoc['Time_Out'] > searchTime\
				, journeysArray\
			))
		elif searchType == 'Under':
			''' Under '''
			glob.LOGGER("[TIME JRNY] Under request")
			print("[TIME JRNY] Under request")
			return list(filter(lambda journeyDoc:\
					'Time_Out' in journeyDoc and journeyDoc['Time_Out'] < searchTime\
				, journeysArray\
			))
		elif searchType == 'Over':
			''' Over '''
			glob.LOGGER("[TIME JRNY] Over request")
			print("[TIME JRNY] Over request")
			return list(filter(lambda journeyDoc:\
					'Time_In' in journeyDoc and  journeyDoc['Time_In'] > searchTime\
				, journeysArray\
			))

	try:
		userRef = glob.COUCH_USER_ACTIVITY[\
			':'.join((glob.PARTITION_KEY_DICT[ Username[0].lower() ], Username))\
		]
		if 'Private' in body.keys():
			''' Private Journeys '''
			res = SeachTimeInJourneysArray(userRef['Private_Journeys'], searchTime, 1)
			glob.LOGGER("[TIME JRNY] Request handled successfully! Response: \n {}".format(str(res)))
			print("[TIME JRNY] Request handled successfully! Response: \n {}".format(str(res)))
			return JsonResponse(res, safe = False)
		else:
			''' Public Journeys '''
			res = SeachTimeInJourneysArray(userRef['Journeys'], searchTime, body['Search_Type'])
			glob.LOGGER("[TIME JRNY] Request handled successfully! Response: \n {}".format(str(res)))
			print("[TIME JRNY] Request handled successfully! Response: \n {}".format(str(res)))
			return JsonResponse(res, safe = False)
	except KeyError:
		glob.LOGGER("[TIME JRNY] User {} has no activity".format(Username))
		print("[TIME JRNY] User {} has no activity".format(Username))
		glob.LOGGER("[TIME JRNY] Request handled successfully! Response: 204")
		print("[TIME JRNY] Request handled successfully! Response: 204")
		return HttpResponse(status = 204)
	except Exception as err:
		glob.LOGGER("[TIME JRNY] Error: \n {}".format(err))
		print("[TIME JRNY] Error: \n {}".format(err))
		return HttpResponse(status = 500)

'''
@csrf_exempt
def IDJourneyHandler(req):
	if not req.body:
		glob.LOGGER("[ID JRNY] Invalid Request: Null body")
		print("[ID JRNY] Invalid Request: Null body")
		return HttpResponse(status = 400)
	body = JSON.loads(req.body)
	if not 'Whos_Asking' in body or not body['Whos_Asking']:
		glob.LOGGER("[ID JRNY] Invalid Request: Missing Whos_Asking")
		print("[ID JRNY] Invalid Request: Missing Whos_Asking")
		return HttpResponse(status = 400)
	if not 'Journey_ID' in body or not body['Journey_ID']:
		glob.LOGGER("[ID JRNY] Invalid Request: Missing Journey_ID")
		print("[ID JRNY] Invalid Request: Missing Journey_ID")
		return HttpResponse(status = 400)

	glob.LOGGER("[ID JRNY] New Request: {}".format(body))
	print("[ID JRNY] New Request: {}".format(body))
	Username = body['Whos_Asking']
	jID = str(body['Journey_ID'])
	# privileged = \
	# bool(body['Username'] == body['Whos_Asking']) if 'Username' in body and 'Whos_Asking' in body else False

	try:
		selector = { "Journeys": { "$elemMatch": { "Journey_ID": Username+':J'+jID } } }
		if 'Private' in body and body['Private']:
			queryRef = list(glob.COUCH_USER_ACTIVITY.get_query_result(selector, fields = ['Private_Journeys']))
			for docs in queryRef:
				for journeyDoc in docs['Private_Journeys']:
					if 'Journey_ID' in journeyDoc and journeyDoc['Journey_ID'] == Username+':J'+jID:
						return JsonResponse(journeyDoc, safe = False)
		else:
			queryRef = list(glob.COUCH_USER_ACTIVITY.get_query_result(selector, fields = ['Journeys']))
			for docs in queryRef:
				for journeyDoc in docs['Journeys']:
					if 'Journey_ID' in journeyDoc and journeyDoc['Journey_ID'] == Username+':J'+jID:
						return JsonResponse(journeyDoc, safe = False)
	except KeyError:
		glob.LOGGER("[ID JRNY] Could not find {} journey id".format(body['Journey_ID']))
		print("[ID JRNY] Could not find {} journey id".format(body['Journey_ID']))
		return HttpResponse(status = 404)
	except Exception as err:
		glob.LOGGER("[ID JRNY] Error @ journey id \n {}".format(err))
		print("[ID JRNY] Error @ journey id \n {}".format(err))
		return HttpResponse(status = 500)
'''

@csrf_exempt
def EditJourneyHandler(req):
	if not req.body:
		glob.LOGGER("[EDIT JRNY] Invalid Request: Null body")
		print("[EDIT JRNY] Invalid Request: Null body")
		return HttpResponse(status = 400)
	body = JSON.loads(req.body)
	if not 'Whos_Asking' in body.keys() or not body['Whos_Asking']:
		glob.LOGGER("[EDIT JRNY] Invalid Request: Missing Whos_Asking")
		print("[EDIT JRNY] Invalid Request: Missing Whos_Asking")
		return HttpResponse(status = 400)
	if not 'Existing_Doc' in body.keys() or not body['Existing_Doc']:
		glob.LOGGER("[EDIT JRNY] Invalid Request: Missing Existing_Doc")
		print("[EDIT JRNY] Invalid Request: Missing Existing_Doc")
		return HttpResponse(status = 400)
	if not 'Changes' in body.keys() or not body['Changes']:
		glob.LOGGER("[EDIT JRNY] Invalid Request: Missing Changes")
		print("[EDIT JRNY] Invalid Request: Missing Changes")
		return HttpResponse(status = 400)

	glob.LOGGER("[EDIT JRNY] New Request {}".format(body))
	print("[EDIT JRNY] New Request {}".format(body))
	
	Username = body['Whos_Asking']
	existingDoc = body['Existing_Doc']
	changes = body['Changes']

	glob.LOGGER("[EDIT JRNY] Request by {}: \n {}".format(Username, body))
	print("[EDIT JRNY] Request by {}: \n {}".format(Username, body))

	try:
		userRef = glob.COUCH_USER_ACTIVITY[\
			':'.join((glob.PARTITION_KEY_DICT[ Username[0].lower() ], Username))\
		]
	except KeyError:
		glob.LOGGER("[EDIT JRNY] User activity not found for {}".format(Username))
		print("[EDIT JRNY] User activity not found for {}".format(Username))
		glob.LOGGER("[EDIT JRNY] Request handled successfully! Response: 404")
		print("[EDIT JRNY] Request handled successfully! Response: 404")
		return HttpResponse(status = 404)
	except Exception as err:
		glob.LOGGER("[EDIT JRNY] Error: \n {}".format(err))
		print("[EDIT JRNY] Error: \n {}".format(err))
		return HttpResponse(status = 500)

	if 'Journeys' in userRef:
		index = userRef['Journeys'].index(existingDoc)
		if index > -1:
			userRef['Journeys'][index].update(changes)
			userRef.save()
			glob.LOGGER("[EDIT JRNY] Updated Journeys of {}".format(Username))
			print("[EDIT JRNY] Updated Journeys of {}".format(Username))

	if 'Private_Journeys' in userRef:
		index = userRef['Private_Journeys'].index(existingDoc)
		if index > -1:
			userRef['Private_Journeys'][index].update(changes)
			userRef.save()
			glob.LOGGER("[EDIT JRNY] Updated Private Journeys of {}".format(Username))
			print("[EDIT JRNY] Updated Private Journeys of {}".format(Username))

	glob.LOGGER("[EDIT JRNY] Request handled successfully! Response: 200")
	print("[EDIT JRNY] Request handled successfully! Response: 200")
	return HttpResponse(status = 200)

@csrf_exempt
def SearchJourneysHandler(req):
	if not req.body:
		glob.LOGGER("[SEARCH JRNY] Invalid Request: Null body")
		print("[SEARCH JRNY] Invalid Request: Null body")
		return HttpResponse(status = 400)
	body = JSON.loads(req.body)
	if 'Whos_Asking' not in body or not body['Whos_Asking']:
		glob.LOGGER("[SEARCH JRNY] Invalid Request: Missing Whos_Asking")
		print("[SEARCH JRNY] Invalid Request: Missing Whos_Asking")
		return HttpResponse(status = 400)
	if 'Search_Term' not in body or not body['Search_Term']:
		glob.LOGGER("[SEARCH JRNY] Invalid Request: Missing Search_Term")
		print("[SEARCH JRNY] Invalid Request: Missing Search_Term")
		return HttpResponse(status = 400)

	searchTerm = body['Search_Term']
	res = []
	
	print("[SEARCH JRNY] Request by {}. Term: {}".format(body['Whos_Asking'], searchTerm))

	# privileged = bool(body['Username'] == body['Whos_Asking']) if 'Username' in body else False

	def SearchForNumber(searchTerm, res):
		try:
			selector = { "Journeys": { "$elemMatch": { "Train_Number": int(searchTerm) } } }
			queryRef = list(glob.COUCH_USER_ACTIVITY.get_query_result(selector, fields = ['key', 'Journeys']))
			for docs in queryRef:
				for jDoc in docs['Journeys']:
					if jDoc['Train_Number'] == int(searchTerm):
						jDoc.update({ 'Username': docs['key'].split(":")[1] })
						# Get Train Number Details
						res.append(jDoc)
		except KeyError:
			glob.LOGGER("[SEARCH JRNY] Could not find {} train number".format(searchTerm))
			print("[SEARCH JRNY] Could not find {} train number".format(searchTerm))
		except Exception as err:
			glob.LOGGER("[SEARCH JRNY] Error @ train number \n {}".format(err))
			print("[SEARCH JRNY] Error @ train number \n {}".format(err))
		
		return res

	def SearchForName(searchTerm):
		return
	def SearchForLocation(searchTerm):
		return

	numberRegx = r"^\d{3,5}$"
	tNameRegx = r"\w{5,}"
	fromToRegex = r"\w{1,4}"
	# usernameRegex = r"(\w{3,}|\w+\|J\d+)"
	# jidRegex = r"\w+\|J\d+"

	if 'Specific_Search' in body.keys() and body['Specific_Search']:
		''' Specific Search '''
		if body['Specific_Search'] == 'Username' and Username in body.keys():
			''' User Specific Search '''
			# if len(re.match(numberRegx))
			return HttpResponse(status = 404)
		elif body['Specific_Search'] == 'Location' and Location in body.keys():
			''' Location Specific Search '''
			return
		else:
			return HttpResponse(status = 400)


	else:
		''' General Search '''

	if 'Private' in body.keys() and body['Private'] and privileged:
		''' Private_Journeys '''
		# if re.match(numberRegx, str())
	else:
		''' Journeys '''
		if re.match(numberRegx, str(searchTerm)):
			''' Search Train_Number '''
			try:
				selector = { "Journeys": { "$elemMatch": { "Train_Number": int(searchTerm) } } }
				queryRef = list(glob.COUCH_USER_ACTIVITY.get_query_result(selector, fields = ['key', 'Journeys']))
				for docs in queryRef:
					for journeyDoc in docs['Journeys']:
						if journeyDoc['Train_Number'] == int(searchTerm):
							journeyDoc.update({'Username': docs['key'].split(":")[1] })
							res.append(journeyDoc)
			except KeyError:
				print("[SEARCH JRNY] Could not find {} train number".format(searchTerm))
			except Exception as err:
				print("[SEARCH JRNY] Error @ train number \n {}".format(err))

	"""
	if 'Username' in body:
		Username = body['Username']
		try:
			userRef = glob.COUCH_USER_ACTIVITY[ ':'.join((glob.PARTITION_KEY_DICT[ Username[0].lower() ], Username)) ]
			res.extend(userRef['Journeys'])
		except KeyError:
			glob.LOGGER("[SEARCH JRNY] User activity not found for {}".format(Username))
			print("[SEARCH JRNY] User activity not found for {}".format(Username))
			return HttpResponse(status = 404)
		except Exception as err:
			glob.LOGGER("[SEARCH JRNY] Error: \n {}".format(err))
			print("[SEARCH JRNY] Error: \n {}".format(err))
			return HttpResponse(status = 500)

	if 'Train_Number' in body:
		selector = {"Journeys": { "$elemMatch": { "Train_Number": int(body['Train_Number']) } } }
		queryRef = list(glob.COUCH_USER_ACTIVITY.get_query_result(selector, fields = ['Journeys']))
		for docs in queryRef:
			for journeyDoc in docs['Journeys']:
				if journeyDoc['Train_Number'] == int(body['Train_Number']):
					if 'Train_Number' in journeyDoc and 'Train_Name' not in journeyDoc:
						trainRef = glob.COUCH_TRAIN_DATA[ str(journeyDoc[ 'Train_Number' ]) ]['Train_Name']
						journeyDoc['Train_Name'] = trainRef
					res.append(journeyDoc)

	if 'From' in body:
		selector = {"Journeys": { "$elemMatch": { "From": body['From'] } } }
		queryRef = list(glob.COUCH_USER_ACTIVITY.get_query_result(selector, fields = ['Journeys']))
		for docs in queryRef:
			for journeyDoc in docs['Journeys']:
				if journeyDoc['From'] == body['From']:
					if 'Train_Number' in journeyDoc and 'Train_Name' not in journeyDoc:
						trainRef = glob.COUCH_TRAIN_DATA[ str(journeyDoc[ 'Train_Number' ]) ]['Train_Name']
						journeyDoc['Train_Name'] = trainRef
					res.append(journeyDoc)
		# res.extend([
		# 	journeyDoc for doc in queryRef for journeyDoc in doc['Journeys']\
		# 	if journeyDoc['From'] == body['From'] 
		# ])

	if 'To' in body:
		selector = {"Journeys": { "$elemMatch": { "To": body['To'] } } }
		queryRef = list(glob.COUCH_USER_ACTIVITY.get_query_result(selector, fields = ['Journeys']))
		for docs in queryRef:
			for journeyDoc in docs['Journeys']:
				if journeyDoc['To'] == body['To']:
					if 'Train_Number' in journeyDoc and 'Train_Name' not in journeyDoc:
						trainRef = glob.COUCH_TRAIN_DATA[ str(journeyDoc[ 'Train_Number' ]) ]['Train_Name']
						journeyDoc['Train_Name'] = trainRef
					res.append(journeyDoc)
		# res.extend([
		# 	journeyDoc for doc in queryRef for journeyDoc in doc['Journeys']\
		# 	if journeyDoc['To'] == body['To'] 
		# ])
	"""

	if not len(res):
		# glob.LOGGER("[SEARCH JRNY] Response: {}".format(res))
		return JsonResponse([], safe = False, status = 204)
	else:
		res.sort(key = lambda doc: doc['Date_Time'], reverse = True)
		# glob.LOGGER("[SEARCH JRNY] Response: {}".format(res))
		return JsonResponse(res, safe = False)