from googleapiclient.discovery import build
import drivepy.config as config
from drivepy.config import MimeTypes
from pprint import pprint
from drivepy.files import GoogleFile

class GoogleDrive(object):
    def __init__(self, authentication):
        """Create an instance of GoogleDrive

        Args:
            authentication: an authentication object to create the service
                        (eg: auth.ServiceAccountAuthentication)
        Returns:
            A GoogleDrive instance
        """
        self.authentication = authentication

        self.service = build('drive', 'v3', http=self.authentication.authorization)

    def list_files(self, **params):
        """List files in a way specified by params

        Args:
            params: a dict-like object, all available parameters for
                    the REST API "files" may be specified here
        Returns:
            A list of files in the drive.
        """
        fields = params.pop('fields', config.ALL_FILE_FIELDS)
        files = self.service.files().list(fields=fields,
                                          **params).execute().get('files')
        return files

    def create_file_from_path(self, path, content=None, mime_type=None, body=None, permissions=None):
        """Creates a file on google drive from a path

        Args:
            path: a file or folder path
            content: a string with the contents of the new file
            mime_type: the type of the file to be created
            permissions: a list of dict-like objects that describe permissions
                        (eg. {'email': 'jap@hotmail.com',
                              'role': PermissionRole.Writer,
                              'type': PermissionType.User}

        Returns:
            A list of the newly created file and it's directories

        Raises:
            A GoogleDriveParameterError if the permissions object is specified and
            there is no 'email' key
        """
        file_sections = path.split('/')

        folders = file_sections[:-1]
        file_name = file_sections[-1]

        parent_id = None

        parent_folders = []

        for folder_name in folders:
            folder_body = {}

            if parent_id:
                folder_body = {'parents': [parent_id]}

            google_file = GoogleFile.get_or_create(self.service, folder_name,
                                                   mime_type=MimeTypes.Folder,
                                                   body=folder_body)

            parent_id = google_file.meta_data['id']
            parent_folders.append(google_file)

        body = body or {}

        if parent_id and 'parents' not in body:
            body.update({'parents': [parent_id]})

        main_file = GoogleFile.get_or_create(self.service, file_name,
                                             mime_type=mime_type,
                                             content=content,
                                             body=body)

        result = parent_folders + [main_file]

        if permissions:
            for permission in permissions:
                email = permission.pop('email', '')
                if not email:
                    raise config.GoogleDriveParameterError('There must be an email key in the permissions object!')
                for google_file in result:
                    google_file.give_permission(email, **permission)

        return result


    def get_file_from_path(self, path):
        """
        Parses a file path into a file query and gets
        the corresponding file objects associated

        Args:
            path: a file path from the root of Google Drive
                  in the form "Folder/SubFolder/file.ext"
        Returns:
            A list of file objects
        """
        file_sections = path.split('/')

        folders = file_sections[:-1]
        file_name = file_sections[-1]

        parent_id = None

        for folder in folders:
            if parent_id:
                folds = self.list_files(q='name = "{}" and "{}" in parents'.format(folder, parent_id),
                                        fields='files/id')
            else:
                folds = self.list_files(q='name = "{}"'.format(folder), fields='files/id')

            if folds:
                fold = folds[0]
                parent_id = fold['id']
            else:
                return []

        files = self.list_files(q='name = "{}" and "{}" in parents'.format(file_name, parent_id))

        result_files = []

        for file_meta in files:
            result_files.append(GoogleFile(self.service, file_meta))

        return result_files
