from oauth2client.service_account import ServiceAccountCredentials
import json
import drivepy.config as config
from httplib2 import Http

class ServiceAuthentication(object):
    """Service Authorization for server-server OAuth2 support

    Fields:
        credentials: ServiceAccountCredentials object loaded from the json file
        authorization: HTTP authorization object
    """
    def __init__(self, auth_file):
        """Creates a ServiceAuthentication object

        Args:
            auth_file: a json file location that contains Google API credentials
        Returns:
            An instance of the ServiceAuthentication object
        """
        credentials = None
        if isinstance(auth_file, file):
            auth_dict = json.load(auth_file)
            credentials = ServiceAccountCredentials.from_json_keyfile_dict(auth_dict,
                                                                           scopes=[config.GOOGLE_DRIVE_SCOPE])
        else:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(auth_file,
                                                                           scopes=[config.GOOGLE_DRIVE_SCOPE])

        self.credentials = credentials
        self.authorization = self.credentials.authorize(Http())
