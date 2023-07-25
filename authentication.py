"""/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Authors:
//		Dasari, Veera Venkata Sairam: VXD210027
        Gnanamoorthy, Vijayan: VXG210040
        Mulkalwar, Ashray: AXM190211
        Satish, Sirisha: SXS210095
        Vunnava, Vaishnavi: VXV210027

// Created date : 4/20/2023
// Description : Google Drive Python file 
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""

import functools
import flask
from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery

#assigning the URL's and keys to the parameters.

ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
AUTHORIZATION_SCOPE ='openid email profile https://www.googleapis.com/auth/drive.file'
AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'

AUTH_REDIRECT_URI = 'http://localhost:6348/google/auth'
BASE_URI = 'http://localhost:6348'

CLIENT_ID = '837027684468-eb3dmc08ll7veccmkn4hbe6d9dcmqd77.apps.googleusercontent.com'
CLIENT_SECRET = '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'

AUTH_TOKEN_KEY = 'auth_token'
AUTH_STATE_KEY = 'auth_state'

app = flask.Blueprint('authentication', __name__)

def checkLogin():
    if AUTH_TOKEN_KEY in flask.session:
        return True
    else:
        False
           
def get_creds():
#defintion used to build credentials from the user
    if not checkLogin():
        raise Exception('User must be logged in')
    oauth2_tokens = flask.session[AUTH_TOKEN_KEY]
    #credentials object  is used to authorize access to Google APIs
    return google.oauth2.credentials.Credentials(
    #The access token and refresh token are obtained from the OAuth2 tokens in the session
                oauth2_tokens['access_token'],
                refresh_token=oauth2_tokens['refresh_token'],
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                token_uri=ACCESS_TOKEN_URI)

def getUserInfo():
#defintion used to get information from the user
    credentials = get_creds()
    get_oauth2Client = googleapiclient.discovery.build(
                        'oauth2', 'v2',
                        credentials=credentials)

    return get_oauth2Client.userinfo().get().execute()#returns user info
    
def NoCache(view):

    @functools.wraps(view)
    def noCacheImplementation(*args, **kwargs):
    #this is a decorator function used for a flask view function
    #  this adds header to the responce to prevent caching
    
        response = flask.make_response(view(*args, **kwargs))
        response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        response.headers.add('Pragma', 'no-cache')
        response.headers.add('Expires', '-1')
        return response
    #returns wrapped function
    return functools.update_wrapper(noCacheImplementation, view)# function used to copy original function name, docs 


@app.route('/google/login')
@NoCache
def login_session():
#sets up the login session for the user using OAuth2
    session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                            scope=AUTHORIZATION_SCOPE,
                            redirect_uri=AUTH_REDIRECT_URI)
  
    uri, state = session.authorization_url(AUTHORIZATION_URL)

    flask.session[AUTH_STATE_KEY] = state
    flask.session.permanent = True

    return flask.redirect(uri, code=302)#returns flask redirect to the authorization url
    
    
@app.route('/google/auth')
@NoCache# prevents the browser from caching the responce to the route
def auth_redirect():
#defintion used to redirect the authorization
    req_state = flask.request.args.get('state', default=None)

    if req_state != flask.session.get(AUTH_STATE_KEY):
        response = flask.make_response('Invalid state parameter', 401)
        return response
    session = OAuth2Session(# if state parameter is invalid
        CLIENT_ID,
        CLIENT_SECRET,
        scope=AUTHORIZATION_SCOPE,
        state=flask.session.get(AUTH_STATE_KEY),
        redirect_uri=AUTH_REDIRECT_URI
    )
    oauth2_tokens = session.fetch_token(
        ACCESS_TOKEN_URI,
        authorization_response=flask.request.url
    )
    flask.session[AUTH_TOKEN_KEY] = oauth2_tokens
    return flask.redirect(BASE_URI, code=302)#user redirects the user back to the homepage of the application
   
    
@app.route('/google/logout')
@NoCache
def logging_out():
# logout from the session using auth_token key
    flask.session.pop(AUTH_TOKEN_KEY, None)
    flask.session.pop(AUTH_STATE_KEY, None)
    flask.session.modified = True
    return flask.redirect(BASE_URI, code=302)# redirected page
