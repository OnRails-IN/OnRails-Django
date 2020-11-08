import os
import json as JSON
from cloudant.client import CouchDB

from django.conf import settings as glob
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

def PopulateDatabase(admin_couch_client, dbName, populate):
	if not admin_couch_client[dbName].exists():
		glob.LOGGER("[POPULATE] {} does not exist!")
		print("[POPULATE] {} does not exist!")
		return False
	else:
		for doc in populate:
			try:
				admin_couch_client[dbName].create_document(doc)
			except Exception as err:
				glob.LOGGER("[POPULATE] Error in creating doc {} \n {}".format(doc, err))
				print("[POPULATE] Error in creating doc {} \n {}".format(doc, err))
		return True

@csrf_exempt
def HealthHandler(req):
	return JsonResponse({ 'success': True, 'health': "Good" })

@csrf_exempt
def CreateDBHandler(req):
	if not req.body:
		glob.LOGGER("[MOD] Invalid Request: Null body")
		print("[MOD] Invalid Request: Null body")
		return HttpResponse(status=400)
	body = JSON.loads(req.body)
	if 'Whos_Asking' not in body or not body['Whos_Asking']:
		glob.LOGGER("[MOD] Invalid Request: Null Whos_Asking")
		print("[MOD] Invalid Request: Null Whos_Asking")
		return HttpResponse(status=400)
	if 'Password' not in body or not body['Password']:
		glob.LOGGER("[MOD] Invalid Request: Null Password")
		print("[MOD] Invalid Request: Null Password")
		return HttpResponse(status=400)
	if 'Database_Name' not in body or not body['Database_Name']:
		glob.LOGGER("[MOD] Invalid Request: Null database name")
		print("[MOD] Invalid Request: Null database name")
		return HttpResponse(status=400)

	glob.LOGGER("[MOD] Create DB request by {}".format(body['Whos_Asking']))
	print("[MOD] Create DB request by {}".format(body['Whos_Asking']))
	populate = body['Populate'] if 'Populate' in body and body['Populate'] is not None else False
	
	try:
		admin_couch_client = CouchDB(
			body['Whos_Asking'],
			body['Password'],
			url = glob.COUCH_HOST+':'+glob.COUCH_PORT,
			connect = True
		)
	except KeyError:
		glob.LOGGER("[MOD] Couch Admin not found")
		print("[MOD] Couch Admin not found")
		return HttpResponse(status=404)
	except Exception as err:
		glob.LOGGER("[MOD] Could not connect to couch as {} \n {}".format(body[ 'Whos_Asking' ], err))
		print("[MOD] Could not connect to couch as {} \n {}".format(body[ 'Whos_Asking' ], err))
		return HttpResponse(status=500)

	try:
		admin_couch_client[ str(body[ 'Database_Name' ]) ].exists()
		glob.LOGGER("[MOD] Database {} already exists".format(body[ 'Database_Name' ]))
		print("[MOD] Database {} already exists".format(body[ 'Database_Name' ]))
		return HttpResponse(status=406)
	except KeyError:
		glob.LOGGER("[MOD] Creating new {} database".format(body[ 'Database_Name' ]))
		print("[MOD] Creating new {} database".format(body[ 'Database_Name' ]))
		admin_couch_client.create_database(body[ 'Database_Name' ])
		if populate:
			if PopulateDatabase(admin_couch_client, body[ 'Database_Name' ], populate):
				return HttpResponse(status=200)
			else:
				return HttpResponse(status=500)

@csrf_exempt
def CreateDocHandler(req):
	if not req.body:
		glob.LOGGER("[MOD] Invalid Request: Null body")
		print("[MOD] Invalid Request: Null body")
		return HttpResponse(status=400)
	body = JSON.loads(req.body)
	if 'Whos_Asking' not in body or not body['Whos_Asking']:
		glob.LOGGER("[MOD] Invalid Request: Null Whos_Asking")
		print("[MOD] Invalid Request: Null Whos_Asking")
		return HttpResponse(status=400)
	if 'Password' not in body or not body['Password']:
		glob.LOGGER("[MOD] Invalid Request: Null Password")
		print("[MOD] Invalid Request: Null Password")
		return HttpResponse(status=400)
	if 'Database_Name' not in body or not body['Database_Name']:
		glob.LOGGER("[MOD] Invalid Request: Null database name")
		print("[MOD] Invalid Request: Null database name")
		return HttpResponse(status=400)
	if 'Populate' not in body or not body['Populate']:
		glob.LOGGER("[MOD] Invalid Request: Null Populate")
		print("[MOD] Invalid Request: Null Populate")
		return HttpResponse(status=400)
	
	glob.LOGGER("[MOD] Create Doc request by {} for {}".format(body['Whos_Asking'], body['Database_Name']))
	print("[MOD] Create Doc request by {} for {}".format(body['Whos_Asking'], body['Database_Name']))

	try:
		admin_couch_client = CouchDB(
			body['Whos_Asking'],
			body['Password'],
			url = glob.COUCH_HOST + ':' + glob.COUCH_PORT,
			connect = True
		)
		glob.LOGGER("[MOD] {} found".format(body[ 'Whos_Asking' ]))
		print("[MOD] {} found".format(body[ 'Whos_Asking' ]))
	except KeyError:
		glob.LOGGER("[MOD] Couch Admin {} not found".format(body[ 'Whos_Asking' ]))
		print("[MOD] Couch Admin {} not found".format(body[ 'Whos_Asking' ]))
		return HttpResponse(status=404)
	except Exception as err:
		glob.LOGGER("[MOD] Could not connect to couch as {} \n {}".format(body[ 'Whos_Asking' ], err))
		print("[MOD] Could not connect to couch as {} \n {}".format(body[ 'Whos_Asking' ], err))
		return HttpResponse(status=500)

	try:
		if type(body['Populate']).__name__ == 'list':
			if PopulateDatabase(admin_couch_client, body['Database_Name'], body['Populate']):
				return HttpResponse(status=201)
		elif type(body['Populate']).__name__ == 'dict':
			if PopulateDatabase(admin_couch_client, body['Database_Name'], [ body['Populate'] ]):
				return HttpResponse(status=201)
		else:
			glob.LOGGER("[MOD] Invalid data type of document {}".format(type(body['Populate']).__name__))
			print("[MOD] Invalid data type of document {}".format(type(body['Populate']).__name__))
			return HttpResponse(status=400)
	except Exception as err:
		glob.LOGGER("[MOD] Error @ Populate \n {}".format(err))
		print("[MOD] Error @ Populate \n {}".format(err))
		return HttpResponse(status=500)

@csrf_exempt
def TruncateDBHandler(req):
	if not req.body:
		glob.LOGGER("[MOD] Invalid Request: Null body")
		print("[MOD] Invalid Request: Null body")
		return HttpResponse(status=400)
	body = JSON.loads(req.body)
	if 'Whos_Asking' not in body or not body['Whos_Asking']:
		glob.LOGGER("[MOD] Invalid Request: Null Whos_Asking")
		print("[MOD] Invalid Request: Null Whos_Asking")
		return HttpResponse(status=400)
	if 'Password' not in body or not body['Password']:
		glob.LOGGER("[MOD] Invalid Request: Null Password")
		print("[MOD] Invalid Request: Null Password")
		return HttpResponse(status=400)
	if 'Database_Name' not in body or not body['Database_Name']:
		glob.LOGGER("[MOD] Invalid Request: Null database name")
		print("[MOD] Invalid Request: Null database name")
		return HttpResponse(status=400)
	
	glob.LOGGER("[MOD] Truncate request by {} for {}".format(body['Whos_Asking'], body['Database_Name']))
	print("[MOD] Truncate request by {} for {}".format(body['Whos_Asking'], body['Database_Name']))
	
	try:
		admin_couch_client = CouchDB(
			body['Whos_Asking'],
			body['Password'],
			url = glob.COUCH_HOST + ':' + glob.COUCH_PORT,
			connect = True
		)
		glob.LOGGER("[MOD] {} found".format(body[ 'Whos_Asking' ]))
		print("[MOD] {} found".format(body[ 'Whos_Asking' ]))
	except KeyError:
		glob.LOGGER("[MOD] Couch Admin {} not found".format(body[ 'Whos_Asking' ]))
		print("[MOD] Couch Admin {} not found".format(body[ 'Whos_Asking' ]))
		return HttpResponse(status=404)
	except Exception as err:
		glob.LOGGER("[MOD] Could not connect to couch as {} \n {}".format(body[ 'Whos_Asking' ], err))
		print("[MOD] Could not connect to couch as {} \n {}".format(body[ 'Whos_Asking' ], err))
		return HttpResponse(status=500)

	try:
		if admin_couch_client[ str(body[ 'Database_Name' ]) ].exists():
			glob.LOGGER("[MOD] Database {} found".format(body[ 'Database_Name' ]))
			print("[MOD] Database {} found".format(body[ 'Database_Name' ]))
		for doc in admin_couch_client[ str(body[ 'Database_Name' ]) ]:
			doc.delete()
		glob.LOGGER("[MOD] Database {} truncated!".format(body[ 'Database_Name' ]))
		print("[MOD] Database {} truncated!".format(body[ 'Database_Name' ]))
		return HttpResponse(status=200)
	except KeyError:
		glob.LOGGER("[MOD] Database {} does not exist to truncate".format(body[ 'Database_Name' ]))
		print("[MOD] Database {} does not exist to truncate".format(body[ 'Database_Name' ]))
		return HttpResponse(status=404)
	except Exception as err:
		glob.LOGGER("[MOD] Error at checking existing DB {}".format(body[ 'Database_Name' ]))
		print("[MOD] Error at checking existing DB {}".format(body[ 'Database_Name' ]))
		return HttpResponse(status=500)

@csrf_exempt
def UpdateDBHandler(req):
	if not req.body:
		glob.LOGGER("[MOD] Invalid Request: Null body")
		print("[MOD] Invalid Request: Null body")
		return HttpResponse(status=400)
	body = JSON.loads(req.body)
	if 'Whos_Asking' not in body or not body['Whos_Asking']:
		glob.LOGGER("[MOD] Invalid Request: Null Whos_Asking")
		print("[MOD] Invalid Request: Null Whos_Asking")
		return HttpResponse(status=400)
	if 'Password' not in body or not body['Password']:
		glob.LOGGER("[MOD] Invalid Request: Null Password")
		print("[MOD] Invalid Request: Null Password")
		return HttpResponse(status=400)
	if 'Database_Name' not in body or not body['Database_Name']:
		glob.LOGGER("[MOD] Invalid Request: Null database name")
		print("[MOD] Invalid Request: Null database name")
		return HttpResponse(status=400)
	if 'Old_Doc' not in body or not body['Old_Doc']:
		glob.LOGGER("[MOD] Invalid Request: Null Old_Doc")
		print("[MOD] Invalid Request: Null Old_Doc")
		return HttpResponse(status=400)
	if 'Update_Doc' not in body or not body['Update_Doc']:
		glob.LOGGER("[MOD] Invalid Request: Null Update_Doc")
		print("[MOD] Invalid Request: Null Update_Doc")
		return HttpResponse(status=400)

	glob.LOGGER("[MOD] Update request by {} \n from {} to {}".format(
			body['Whos_Asking'],
			body['Old_Doc'],
			body['Update_Doc'])
	)
	print("[MOD] Update request by {} \n from {} to {}".format(body['Whos_Asking'], body['Old_Doc'], body['Update_Doc']))

	try:
		admin_couch_client = CouchDB(
			body['Whos_Asking'],
			body['Password'],
			url = glob.COUCH_HOST + ':' + glob.COUCH_PORT,
			connect = True
		)
		glob.LOGGER("[MOD] {} found".format(body[ 'Whos_Asking' ]))
		print("[MOD] {} found".format(body[ 'Whos_Asking' ]))
	except KeyError:
		glob.LOGGER("[MOD] Couch Admin {} not found".format(body[ 'Whos_Asking' ]))
		print("[MOD] Couch Admin {} not found".format(body[ 'Whos_Asking' ]))
		return HttpResponse(status=404)
	except Exception as err:
		glob.LOGGER("[MOD] Could not connect to couch as {} \n {}".format(body[ 'Whos_Asking' ], err))
		print("[MOD] Could not connect to couch as {} \n {}".format(body[ 'Whos_Asking' ], err))
		return HttpResponse(status=500)

	if 'Update_Factor' in body:
		try:
			index = admin_couch_client[ str(body['Database_Name']) ][ body['Update_Factor'] ].index(body[ 'Old_Doc' ])
			admin_couch_client[ str(body['Database_Name']) ][ body['Update_Factor'] ][index].update(body['Update_Doc'])
			admin_couch_client[ str(body['Database_Name']) ].save()
			glob.LOGGER("[MOD] {} changes updated".format(body[ 'Update_Doc' ]))
			print("[MOD] {} changes updated".format(body[ 'Update_Doc' ]))
			return HttpResponse(status=200)
		except KeyError:
			glob.LOGGER("[MOD] Old doc not found in {}/{}".format(body[ 'Database_Name' ], body[ 'Update_Factor' ]))
			print("[MOD] Old doc not found in {}/{}".format(body[ 'Database_Name' ], body[ 'Update_Factor' ]))
			return HttpResponse(status=404)
		except Exception as err:
			glob.LOGGER("[MOD] Error finding old doc \n {}".format(err))
			print("[MOD] Error finding old doc \n {}".format(err))
			return HttpResponse(status=500)
	else:
		try:
			for doc in admin_couch_client[ str(body[ 'Database_Name' ]) ]:
				if doc == body['Old_Doc']:
					doc.update(body['Update_Doc'])
					doc.save()
			glob.LOGGER("[MOD] {} changes updated".format(body[ 'Update_Doc' ]))
			print("[MOD] {} changes updated".format(body[ 'Update_Doc' ]))
			return HttpResponse(status=200)
		except KeyError:
			glob.LOGGER("[MOD] Old doc not found in {}/{}".format(body[ 'Database_Name' ], body[ 'Update_Factor' ]))
			print("[MOD] Old doc not found in {}/{}".format(body[ 'Database_Name' ], body[ 'Update_Factor' ]))
			return HttpResponse(status=404)
		except Exception as err:
			glob.LOGGER("[MOD] Error finding old doc \n {}".format(err))
			print("[MOD] Error finding old doc \n {}".format(err))
			return HttpResponse(status=500)

"""
@csrf_exempt
def CreateModHandler(req):
	if not req.body:
		glob.LOGGER("[MOD] Invalid Request: Null body")
		print("[MOD] Invalid Request: Null body")
		return HttpResponse(status=400)
	body = JSON.loads(req.body)
	if 'Whos_Asking' not in body or not body['Whos_Asking']:
		glob.LOGGER("[MOD] Invalid Request: Null Whos_Asking")
		print("[MOD] Invalid Request: Null Whos_Asking")
		return HttpResponse(status=400)
	if 'Password' not in body or not body['Password']:
		glob.LOGGER("[MOD] Invalid Request: Null Password")
		print("[MOD] Invalid Request: Null Password")
		return HttpResponse(status=400)
	if 'New_Moderator' not in body or not body['New_Moderator']:
		glob.LOGGER("[MOD] Invalid Request: Null New_Moderator")
		print("[MOD] Invalid Request: Null New_Moderator")
		return HttpResponse(status=400)
	if 'List_Of_Databases' not in body or not body['List_Of_Databases']:
		glob.LOGGER("[MOD] Invalid Request: Null database list mentioned")
		print("[MOD] Invalid Request: Null database list mentioned")
		return HttpResponse(status=400)

	try:
		admin_couch_client = CouchDB(
			body['Whos_Asking'],
			body['Password'],
			url = glob.COUCH_HOST + ':' + glob.COUCH_PORT,
			connect = True
		)
	except KeyError:
		glob.LOGGER("[MOD] Admin user not found")
		print("[MOD] Admin user not found")
		return HttpResponse(status=404)
	except Exception as err:
		glob.LOGGER("[MOD] Error connecting as admin \n {}".format(err))
		print("[MOD] Error connecting as admin \n {}".format(err))
		return HttpResponse(status=500)

	newMod = body['New_Moderator']
	dbList = body['List_Of_Databases']
	glob.LOGGER("[MOD] New Moderator request")
	print("[MOD] New Moderator request")
	
	try:
		# Creating record in _users table
		newMod[ '_id' ] = 'org.couchdb.user:' + newMod[ 'name' ]
		newMod[ 'key' ] = 'org.couchdb.user:' + newMod[ 'name' ]
		admin_couch_client[ '_users' ].create_document(newMod)
		glob.LOGGER("[MOD] New Moderator {} created".format(newMod[ 'name' ]))
		print("[MOD] New Moderator {} created".format(newMod[ 'name' ]))

		# Setting DB permissions manually
		for dbName in dbList:
			os.system("curl -u {}:{} -X PUT {}:{}/{}/_security")
		curlReq = "curl -u {}:{} -X GET {}:{}/{}/_security"
		return HttpResponse(status=201)
	except Exception as err:
		glob.LOGGER("Error creating new moderator \n {}".format(err))
		print("Error creating new moderator \n {}".format(err))
		return HttpResponse(status=500)
"""