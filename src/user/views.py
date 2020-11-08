from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as glob
import json as JSON
import time as TIME

''' Setting Encryption  '''
from cryptography.fernet import Fernet
Encryption = Fernet(glob.ENCRYPT_KEY.encode())

@csrf_exempt
def LoginHandler(req):
	if not req.body:
		print("[LOGIN] Empty request body")
		return HttpResponse(status=400)
	body = JSON.loads(req.body)
	
	if not 'Username' in body.keys() or not body['Username']:
		print("[LOGIN] Invalid Username request")
		return HttpResponse(status=400)
	if not 'Password' in body.keys() or not body['Password']:
		print("[LOGIN] Invalid Password request")
		return HttpResponse(status=400)
	
	print("[LOGIN] New request \n {}".format(body))
	
	try:
		''' Find Username '''
		userRef = glob.COUCH_USER_INFO[\
			':'.join((glob.PARTITION_KEY_DICT[ body['Username'][0].lower() ], body['Username']))\
		]
		''' Check Password '''
		if Encryption.decrypt(userRef['Password'].encode()).decode() != body['Password']:
			print("[LOGIN] Wrong Password")
			return HttpResponse("Wrong Password", status=403)
		else:
			print("[LOGIN] User {} logged in successfully!".format(body['Username']))
			return HttpResponse(status=200)
	except KeyError:
		print("[LOGIN] Username {} was not found".format(body['Username']))
		return HttpResponse("Username Not Found", status=401)
	except Exception as err:
		print("[LOGIN] Error: \n {}".format(err))
		return HttpResponse("Error", status=500)

@csrf_exempt
def SignupHandler(req):
	if not req.body:
		print("[SIGNUP] Empty request body")
		return HttpResponse(status=400)
	body = JSON.loads(req.body)
	
	if not 'Username' in body.keys() or not body['Username']:
		print("[SIGNUP] Invalid Username request")
		return HttpResponse(status=400)
	if not 'Password' in body.keys() or not body['Password']:
		print("[SIGNUP] Invalid Password request")
		return HttpResponse(status=400)
	if not 'Email' in body.keys() or not body['Email']:
		print("[SIGNUP] No email address mentioned")

	print("[SIGNUP] New request \n {}".format(body))


	signupDoc = { k:v for k,v in body.items() if v }
	signupDoc['Password'] = Encryption.encrypt(signupDoc['Password'].encode()).decode()
	if 'Display_Name' not in signupDoc.keys():
		signupDoc['Display_Name'] = body['Username']
	signupDoc['Created'] = int(TIME.time())
	signupDoc['_id'] = ':'.join((glob.PARTITION_KEY_DICT[ body['Username'][0].lower() ], body['Username']))
	signupDoc['key'] = ':'.join((glob.PARTITION_KEY_DICT[ body['Username'][0].lower() ], body['Username']))
	
	print(JSON.dumps(signupDoc, indent=4))

	try:
		glob.COUCH_USER_INFO.create_document(signupDoc)
		print("[SIGNUP] User {} created successfully!".format(body['Username']))
		return HttpResponse(status=200)
	except Exception as err:
		print("[SIGNUP] Error: \n {}".format(err))
		return HttpResponse(status=500)

@csrf_exempt
def ListUsernamesHandler(req):
	try:
		userRef = glob.COUCH_USER_INFO.all_docs(include_docs=True)['rows']
		# print(JSON.dumps(result, indent=2))
		if len(list(userRef)) < 1:
			print("[LIST USERNAMES] Error: No users yet")
			return HttpResponse(status=204)
		else:
			usernames = [row['doc']['Username'] if row['doc']['Username'] else None for row in userRef]
			return JsonResponse(usernames, safe=False)
	except Exception as err:
		print("[LIST USERNAMES] Error: \n {}".format(err))
		return HttpResponse(status=500)

@csrf_exempt
def UserAchievementsHandler(req):
	if not req.body:
		print("[ACHIEVEMENTS] Empty request body")
		return HttpResponse(status=400)
	body = JSON.loads(req.body)
	try:
		Username = body['Username']
		uAchievements = glob.COUCH_USER_INFO[\
			':'.join((glob.PARTITION_KEY_DICT[ Username[0].lower() ], Username))\
		]['Achievements']
		return JsonResponse(list(uAchievements), safe=False)
	
	except Exception as err:
		print("[ACHIEVEMENTS] Error: \n {}".format(err))
		return HttpResponse(status=500)