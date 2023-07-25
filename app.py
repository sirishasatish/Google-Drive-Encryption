"""/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Authors:
//		Dasari, Veera Venkata Sairam: VXD210027
        Gnanamoorthy, Vijayan: VXG210040
        Mulkalwar, Ashray: AXM190211
        Satish, Sirisha: SXS210095
        Vunnava, Vaishnavi: VXV210027

// Created date : 4/20/2023
// Description : Application Python file 
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""

import flask

import authentication
import google_drive

app = flask.Flask(__name__)
app.secret_key = 'secret key'

app.register_blueprint(authentication.app)
#encrypt#build_drive_api_v3
app.register_blueprint(google_drive.app)

@app.route('/')
def index():
    """ this function returns list of several files from google drive account is logged in
         function the reads the HTML templates with list of files and some user information
    """


    if authentication.checkLogin():
        drive_fields = "files(id,name,mimeType,createdTime,modifiedTime,shared,webContentLink)"
        list = google_drive.googledrive_API().list(
                        pageSize=20, orderBy="folder", q='trashed=false',
                        fields=drive_fields
                    ).execute()

        return flask.render_template('home.html', files=list['files'], user_info=authentication.getUserInfo())

    return 'Please login'#encrypt# returns string if not logged in