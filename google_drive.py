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
#logging_out
import io
import tempfile

import flask
import os
from urllib.parse import urlparse

from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import scrypt

from apiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import googleapiclient.discovery
from authentication import get_creds, getUserInfo#google_auth
import gdown
from werkzeug.utils import secure_filename


import authentication
import os#auth_redirect

app = flask.Blueprint('google_drive', __name__)

def encryption(input_file,input_pswd,input_doc):

#definition is to encrypt the file by sending input file, password as the parameters

    Data_Buffer = 1024 * 1024 
    
    """  This is an encryption using AES (Advanced Encryption Standard) algorithm
                           in GCM (Galois Counter Mode) mode.  
    """

    password = input_pswd  
    # temporary folder is created to store the data
    output_file = tempfile.TemporaryFile()

    """  Salt is used to generate random bits
         key is generated using selected password and random bits(salt)
                  
    """

    salt = get_random_bytes(32)  
    key = scrypt(password, salt, key_len=32, N=2 ** 17, r=8, p=1)  
    output_file.write(salt)  # salt is uploaded into the output file
    
    """  object chipher encryts the each chunk of data using AES.new using GCM mode
         The function then reads the reads the input file in chunks of data_buffer.
         Encryted file sent into the output file.
    """

    cipher = AES.new(key, AES.MODE_GCM)
    output_file.write(cipher.nonce)
    """encrypted_data has the ecrypted  data
    #   Output_file has the data that is encryted\
    #   encrypting the data till the last chunck
    """
    data_buff = input_doc.read(Data_Buffer)
    while len(data_buff) != 0:  
        encrypted_data = cipher.encrypt(data_buff)  
        output_file.write(encrypted_data)  
        data_buff = input_doc.read(Data_Buffer)  
    # digest() method from the cipher object generates a tag and writes into the output file
    tag = cipher.digest()  
    output_file.write(tag)
   
    input_doc.close()
    

    return output_file# returns output file

def decryption(outputfile,input_pswd,input_doc,key=None):
#definition is to decyptes the file by sending input file, password as the parameters
         
         
    """  This is an decryption using AES (Advanced Encryption Standard) algorithm
                           in GCM (Galois Counter Mode) mode.  
    """
    Data_Buffer = 1024 * 1024
   
    password = input_pswd  
    
    """  Salt is used to generate random bits-32 bits
         key is generated using selected password and random bits(salt)
         decrypted file is used as the input file
                  
    """

    output_filename = outputfile 
    input_doc.seek(0, os.SEEK_END)
    input_file_size = input_doc.tell()
    input_doc.seek(0)
    # Open files
    input_doc = input_doc
    output_file = tempfile.TemporaryFile()
    salt = input_doc.read(32)  

    # Read salt and generate key
    
    """  Reads in the salt and nonce from the input document
         generates a key from the password salt using the scrypt algorithm.
         It then creates an AES cipher object using the generated key and nonce.
         # Total - salt - nonce - tag = encrypted data
    """
    
    
    if not key:
        key = scrypt(password, salt, key_len=32, N=2 ** 17, r=8, p=1)  
    
    nonce = input_doc.read(16) 
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    
    file_size = input_file_size
    total_encrypted_data = file_size - 32 - 16 - 16 
  
    
    """ size of the encrypted data is calculated  in the input document
        Reads in the encrypted data in chunks of a pre-defined buffer size
        then Decrypts each chunk of data using the AES cipher object
        Writes the decrypted data to the output file
    """
    
    for _ in range(
            int(total_encrypted_data/ Data_Buffer)): 
        data = input_doc.read(Data_Buffer)  
        data_decrypted = cipher.decrypt(data)  
        output_file.write(data_decrypted)  
    data = input_doc.read(
        int(total_encrypted_data % Data_Buffer))  
    data_decrypted = cipher.decrypt(data)  
    output_file.write(data_decrypted)  


    """ this functions verifies the integrity of the decrypted file by comparing its tag
           tags are retrived from the input document
           if tags doesn't match the function raises a ValueError and deletes the temporary output file.    
    """
    tag = input_doc.read(16)
    try:
        cipher.verify(tag)
    except ValueError as e:
        
        input_doc.close()
        output_file.close()
        try:
            os.remove(output_filename)
        except Exception as error:
            pass

        raise e

    
    input_doc.close()
    
    return output_file,key# returns the output file and key

def googledrive_API():
#definition used to build drive api with certain credentials
    credentials = get_creds()
    return googleapiclient.discovery.build('drive', 'v3', credentials=credentials).files()

def authorization_request(file_id):
#definition used to set permissions for the files with ID's
    services = googledrive_SERVICE()
    try:
        authorization = {'type': 'anyone',# authorization
                      'value': 'anyone',
                      'role': 'reader'}
        return services.permissions().create(fileId=file_id,body=authorization).execute()
    except HttpError as error:
        return print('Error while authorization:', error)
    
    
def googledrive_SERVICE():
    credentials = get_creds()
    return googleapiclient.discovery.build('drive', 'v3', credentials=credentials)


def image_storage(file_name, media_type, file_data,file_id=None):#image_storage
    google_drive_api = googledrive_API()
    generate_ids_result = google_drive_api.generateIds(count=1).execute()
    file_id_new = generate_ids_result['ids'][0]

    if not file_id:
        body = {
            'id': file_id_new,
            'name': file_name,
            'mimeType': media_type,
            "role": "reader",
            "type": "anyone",
            'value': '',
        }
    else:
        body = {
            'name': file_name,
            'mimeType': media_type,
            "role": "reader",
            "type": "anyone",
            'value': '',
        }
    media_body = MediaIoBaseUpload(file_data,
                                   mimetype=media_type,
                                   resumable=True)
    if not file_id:
        google_drive_api.create(body=body,
                         media_body=media_body,
                         fields='id,name,mimeType,createdTime,modifiedTime').execute()
        file_id = file_id_new
    else:
        google_drive_api.update(fileId =file_id,body=body,
                         media_body=media_body,
                         fields='id,name,mimeType,createdTime,modifiedTime').execute()
    authorization_request(file_id)
    return file_id

@app.route('/drive/upload-file', methods=['GET', 'POST'])
def upload_file():########################################################
# this defintion is to upload the document into the drive/server
    if 'file' not in flask.request.files:
        return flask.redirect('/')

    file = flask.request.files['file']
    if (not file):
        return flask.redirect('/')
    """Before uploading:
             File has to be uploded from a folder
             Password has to be setup before uploading 
             Flask web framework is used
    """
    password = flask.request.form.get('password')
    filename = secure_filename(file.filename)
    output_file = encryption(filename,password,file)
    output_file.seek(0)
    

    media_type = flask.request.headers['Content-Type']
    image_storage(filename, media_type, output_file,file_id=None)

    return flask.redirect('/')#######################################################3

@app.route('/drive/view-file/<file_id>&<method>', methods=['GET','POST'])
def access_file(file_id, method):
#defintion access the file in the action section 

    # retriving the password from flask request
    if flask.request.method == 'GET':
        google_drive_api = googledrive_API()

        metadata = google_drive_api.get(fields="name,mimeType,webViewLink", fileId=file_id).execute()
        file_n = metadata['name']
        print(method)

        return flask.render_template('update.html', file_content='',
                                     user_info=getUserInfo(),file_id=file_id, file_n= file_n, method= method)



    google_drive_api = googledrive_API()

    attributes = google_drive_api.get(fields="name,mimeType,webViewLink", fileId=file_id).execute()

    request = google_drive_api.get_media(fileId=file_id)
    file_Share = io.BytesIO()
    """Edit/share request is added in the section 
       Retrieve file: file can be edited
       share file: file is edited and uploaded into the drive 
    """
    uploader = MediaIoBaseDownload(file_Share, request)

    done = False
    while done is False:
        status, done = uploader.next_chunk()

    file_Share.seek(0)
    file_name = attributes['name']
    password = flask.request.form.get("password")
    
    """File is decrytped with file name and password associated with it 
    """
    try:
        output_file,key = decryption(file_name,password,file_Share,key=None)
        output_file.seek(0)
        
        """Flask web framework is used read contents of the file specified in the output_file. 
           This returns .html template rendered with certain values passed into it
           Update.html template uses variables to display information on the page, such as contents of a file, 
            the user's information and a shareable URL.
        """
    except ValueError as e:
        return flask.render_template('update.html', file_content="Wrong Password or Illegally Edited",
                                     user_info=getUserInfo(), file_name=file_name, method = "view")

    if flask.request.form.get("share", None):
      
        share_url = attributes['webViewLink']
        return flask.render_template('update.html', share_url=share_url,
                                     user_info=getUserInfo(), share=True, key=key.hex())

    print(method)
    return  flask.render_template('update.html', file_content=output_file.read().decode("utf-8") ,
                                  user_info=getUserInfo(), file_name = file_name,
                                  file_id=file_id,password = password, method= method)

@app.route('/drive/delete/<file_id>', methods=['GET'])
def delete_file(file_id):
#defintion to delete the file which is already uploaded
    google_drive_api = googledrive_API()
    google_drive_api.delete(fileId=file_id).execute()

    return flask.redirect('/')

@app.route('/drive/save/<file_id>', methods=['POST'])
def update_file(file_id):
# definition for updating the file which is already updated
    google_drive_api = googledrive_API()

    attributes = google_drive_api.get(fields="name,mimeType", fileId=file_id).execute()
    file_name = attributes['name']
    #requesting password and content using flask
    password = flask.request.form.get("password")
    content = flask.request.form.get("content")
    #tempory file is created to store the output data
    output_file = tempfile.TemporaryFile()
    #writing into the temperory file
    output_file.write(content.encode('utf-8'))
    output_file.seek(0)
    #file is encruted from the file name and given password and ouptput is stored in output_file
    output_file = encryption(file_name, password, output_file)
    output_file.seek(0)
    media_type = flask.request.headers['Content-Type']
    # printing out the file key
    print(file_id)
    image_storage(file_name, media_type, output_file,file_id=file_id)

    return flask.redirect('/')

def download_file_from_google_drive(url, target):
# defintion for downloading file from drive
        gdown.download(url, target, quiet=False)

        return target

@app.route('/drive/access-file', methods=['GET','POST'])
def view_shared_file():


    # password is retrived from the flask
    if flask.request.method == 'GET':
        return flask.render_template('fetch.html', file_content='',
                                    user_info=getUserInfo(), view_share=True)
    #secret key is requested from URL
    secretKey = flask.request.form.get("secretKey")
    URL = flask.request.form.get("fileUrl")
    print(URL)# URL is printed
    a = urlparse(URL)
    #Tempory file is created for the output file
    output_file = tempfile.TemporaryFile()
    file_name = os.path.basename(a.path)
    # shared file is retrived from the google drive from below link
    URL =  "https://drive.google.com/uc?id={}".format(URL.split("/")[5])
    download_file_from_google_drive(URL, output_file)# can be downloaded from the drive from the previous defintion
    #getting the output files
    output_file.seek(0)

    try:
    #the file is decrypted with file name and from the URL provided
        output_file,key = decryption(file_name,'',output_file,key=bytes.fromhex(secretKey))
        output_file.seek(0)
        return {"response": output_file.read().decode("utf-8")}
    except ValueError as e:#exceptional cases
        print(str(e))
        return {"response ERROR":"Data is encrypted"}

