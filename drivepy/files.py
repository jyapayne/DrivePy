from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from drivepy.config import MimeTypes, PermissionType, PermissionRole
import drivepy.config as config
import io

class GoogleFile(object):
    """An object representing a file on GoogleDrive"""
    def __init__(self, service, meta_data):
        """Create an instance of a GoogleFile

        Args:
            service: the api service object
            metadata: the metadata for the file

        Returns:
            An instance of GoogleFile
        """

        self.meta_data = meta_data
        self.service = service
        self.content = ''

    @staticmethod
    def create(service, name, mime_type=None, content=None, body=None, **params):
        """Creates a new file in GoogleDrive

        Args:
            service: the API service object
            name: the name of the file, including the extension
            mime_type: the mimetype of the file. See config.MimeTypes
            content: the content string of the file
            body: a dict-like object, describes additional request body args
            params: any additional parameters to send to the API

        Returns:
            A GoogleFile object
        """
        fields = config.ALL_SINGLE_FILE_FIELDS

        body = body or {}
        body.update({'name': name})

        mime_type = mime_type or body.get('mimeType')

        if mime_type is not None:
            body['mimeType'] = mime_type
        else:
            guess = MimeTypes.guess_type(name)
            if guess is not None:
                body['mimeType'] = guess

        create_params = {}

        if content:
            utf_content = content
            try:
                utf_content = content.encode('utf-8')
            except UnicodeDecodeError:
                pass
            cont = io.BytesIO(utf_content)
            media_body = MediaIoBaseUpload(cont,
                                           body['mimeType'],
                                           resumable=True)
            create_params['media_body'] = media_body

        meta_data = service.files().create(body=body, fields=fields, **create_params).execute()

        google_file = GoogleFile(service, meta_data)
        google_file.content = content

        return google_file

    @staticmethod
    def get_or_create(service, name, mime_type=None, content=None, body=None, **params):
        """Gets a file in GoogleDrive or creates it if it doesn't exist

        Args:
            service: the API service object
            name: the name of the file, including the extension
            mime_type: the mimetype of the file. See config.MimeTypes
            content: the content string of the file
            body: a dict-like object, describes additional request body args
            params: any additional parameters to send to the API

        Returns:
            A GoogleFile object
        """

        list_fields = config.ALL_FILE_FIELDS

        body = body or {}
        body.update({'name': name})

        query = 'name = "{}"'.format(name)

        parents = body.get('parents', [])

        if parents:
            parent_id = parents[0]
            query = 'name = "{}" and "{}" in parents'.format(name, parent_id)

        files = service.files().list(fields=list_fields, q=query).execute().get('files')

        if files:
            meta_data = files[0]
            google_file = GoogleFile(service, meta_data)
            return google_file
        else:
            return GoogleFile.create(service, name,
                                     mime_type=mime_type,
                                     content=content,
                                     body=body, **params)

    def refresh(self):
        """Gets the meta data of the file from Google Drive

        Returns:
            The meta data of the file
        """
        fields = config.ALL_SINGLE_FILE_FIELDS
        self.meta_data = self.service.files().get(fileId=self.meta_data['id'], fields=fields).execute()
        return self.meta_data

    def give_permission(self, email, send_notification=False,
                        email_message='', fields=None, **params):
        """Gives permission to an email to view a file

        Args:
            email: a valid Google email address
            send_notification: whether to send an email about the share
            email_message: the contents of the email
            fields: a string with comma separated field names to include
            params: a dict-like object of parameters that can be passed to the api call

        Returns:
            Meta data from the api call
        """
        new_params = {'role': PermissionRole.Reader,
                      'type': PermissionType.User}
        new_params.update(params)
        new_params['emailAddress'] = email

        fields = fields or config.ALL_PERMISSION_FIELDS

        file_id = self.meta_data.get('id')

        permission_service = self.service.permissions()

        email_params = {}
        if email_message:
            email_params['emailMessage'] = email_message

        res = permission_service.create(
            fileId=file_id,
            sendNotificationEmail=send_notification,
            fields=fields,
            body=new_params,
            **email_params
        ).execute()

        self.refresh()

        return res

    def download(self, mime_type=None):
        """Download the content of the file from Google Drive

        Args:
            mime_type: the mime type of the file to download.
                      see here:
                      https://developers.google.com/drive/v3/web/manage-downloads#downloading_google_documents

        Returns:
            The content of the file
        """

        if mime_type is None:
            download_type = MimeTypes.get_download_type(self.meta_data['mimeType'])
        else:
            download_type = mime_type

        req = self.service.files().export_media(fileId=self.meta_data['id'],
                                                mimeType=download_type)
        data = io.BytesIO()
        downloader = MediaIoBaseDownload(data, req)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        data.seek(0)
        self.content = data.read()

        return self.content

    def delete(self):
        """Delete the file on Google Drive

        Returns:
            Metadata for the deleted file
        """
        return self.service.files().delete(fileId=self.meta_data['id']).execute()

    def update(self, meta_data, content=None):
        """Update the current file meta data and contents on Google Drive

        Args:
            meta_data: A dict-like object, updates the current meta data from
                       this data
            contents: A string that replaces the contents of the current file
                      on Google Drive

        Returns:
            Metadata from the file update
        """
        self.meta_data.update(meta_data)
        file_id = self.meta_data['id']

        params = {}

        if content:
            utf_content = content
            try:
                utf_content = content.encode('utf-8')
            except UnicodeDecodeError:
                pass
            cont = io.BytesIO(utf_content)
            media_body = MediaIoBaseUpload(cont,
                                           self.meta_data['mimeType'],
                                           resumable=True)
            params['media_body'] = media_body
            self.content = content

        res = self.service.files().update(fileId=file_id,
                                          body=self.meta_data,
                                          **params).execute()
        return res
