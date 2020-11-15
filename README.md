
OnRails Django
=

App is at that stage where everything works just fine, but isn't too great or clean or impressive.

Will get better in some time!

## Tech stack
**Database**: Couch DB

**Handlers & Routing**: Django & Python

## API Endpoints
Optional fields are marked with *

### User
**Signup**
```
API: /user/signup/
Method: POST
Request Format: {
	Username:		string,
	Password:		string,
	Email*:			email id,
	Display_Name*:	string
}
```
**Login**
```
API: /user/login/
Method: POST
Request Format: { Username: string, Password: string }
```
**All Usernames**
```
API: /user/all/
Method: GET, POST
```
**User Achievements**
```
API: /user/achievements/
Method: GET, POST
Request Format: { Username: string }
```
### Spottings
**New Spotting**
```
API: /spotting/new/
Request Format: {
	Whos_Asking:		string (login username),
	Train_Number:		int,
	Loco_Number:		int,
	Spotting_Time*:		Unix timestamp,
	Spotting_Remarks*:	string
}
```
**List spotting**
```
API: /spotting/list/
Method: GET
Request Format: { Loco_Number: int / Train_Number: int / Train_Name: string }
```
**User spotting**
```
API: /spotting/user/
Method: GET
Request Format: { Username: string, Whos_Asking: string (login username) }
```
**Edit spotting**
```
API: /spotting/edit/
Method: PUT
Request Format: { Username: string, Existing_Doc: JSON object, Edits: JSON object }
```
**Search Spotting**
```
API: /spotting/search/
Method: GET
Request Format: { Search_Term: string }
```
### Journeys
### Method