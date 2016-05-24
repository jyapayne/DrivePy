import mimetypes
import os

GOOGLE_DRIVE_SCOPE = 'https://www.googleapis.com/auth/drive'

ALL_FILE_FIELDS = 'files,kind,nextPageToken'

ALL_SINGLE_FILE_FIELDS = 'appProperties,capabilities,contentHints,createdTime,description,explicitlyTrashed,fileExtension,folderColorRgb,fullFileExtension,headRevisionId,iconLink,id,imageMediaMetadata,isAppAuthorized,kind,lastModifyingUser,md5Checksum,mimeType,modifiedByMeTime,modifiedTime,name,originalFilename,ownedByMe,owners,parents,permissions,properties,quotaBytesUsed,shared,sharedWithMeTime,sharingUser,size,spaces,starred,thumbnailLink,trashed,version,videoMediaMetadata,viewedByMe,viewedByMeTime,viewersCanCopyContent,webContentLink,webViewLink,writersCanShare'

ALL_PERMISSION_FIELDS = 'allowFileDiscovery,displayName,domain,emailAddress,id,kind,photoLink,role,type'

class PermissionRole(object):
    Reader = 'reader'
    Writer = 'writer'
    Owner = 'owner'
    Commenter = 'commenter'

class PermissionType(object):
    User = 'user'
    Group = 'group'
    Domain = 'domain'
    Anyone = 'anyone'

class DownloadType(object):
    # Documents
    HTML = 'text/html'
    RichText = 'text/rtf'
    OpenOfficeDoc = 'application/vnd.oasis.opendocument.text'
    WordDoc = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

    # Spreadsheets
    CSV = 'text/csv'
    Excel = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    OpenOfficeSheet = 'application/x-vnd.oasis.opendocument.spreadsheet'

    # Drawings
    JPEG = 'image/jpeg'
    PNG = 'image/png'
    SVG = 'image/svg+xml'

    # Presentations
    PowerPoint = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'

    # Scripts
    JSON = 'application/vnd.google-apps.script+json'

    # All except Scripts
    PDF = 'application/pdf'

    # All except scripts and sheets
    PlainText = 'text/plain'

class MimeTypes(object):
    Audio = 'application/vnd.google-apps.audio'
    Document = 'application/vnd.google-apps.document'
    Drawing = 'application/vnd.google-apps.drawing'
    File = 'application/vnd.google-apps.file'
    Folder = 'application/vnd.google-apps.folder'
    Form = 'application/vnd.google-apps.form'
    FusionTable = 'application/vnd.google-apps.fusiontable'
    Map = 'application/vnd.google-apps.map'
    Photo = 'application/vnd.google-apps.photo'
    Presentation = 'application/vnd.google-apps.presentation'
    Script = 'application/vnd.google-apps.script'
    Sites = 'application/vnd.google-apps.sites'
    Spreadsheet = 'application/vnd.google-apps.spreadsheet'
    Unknown = 'application/vnd.google-apps.unknown'
    Video = 'application/vnd.google-apps.video'

    TypeDict = {}

    types = {
        Audio: ['mp3', 'wav', 'aac', 'ogg', 'wma'],
        Document: ['txt', 'doc', 'docx', 'log', 'odt', 'rtf'],
        Folder: [''],
        Presentation: ['ppt', 'pptx'],
        Spreadsheet: ['csv', 'xls', 'xlsx', 'xlt', 'xml', 'ods'],
        Video: ['flv', 'mp4', 'mpg', 'mov', 'mkv', 'avi']
    }

    for mime, exts in types.items():
        for ext in exts:
            TypeDict[ext] = mime

    DownloadTypeDict = {
        Document: DownloadType.WordDoc,
        Spreadsheet: DownloadType.Excel,
        Drawing: DownloadType.PDF,
        Presentation: DownloadType.PowerPoint,
        Script: DownloadType.JSON
    }

    @staticmethod
    def get_download_type(mime_type):
        """Tries to guess the download type based on the mime_type."""
        return MimeTypes.DownloadTypeDict.get(mime_type, 'text/plain')

    @staticmethod
    def guess_type(path):
        """Guesses the mimetype of a file extension

        Args:
            path: the file name or path

        Returns:
            A mimetype string
        """
        ext = os.path.split(path)[-1].replace('.', '')
        guess = MimeTypes.TypeDict.get(ext)

        if guess is None:
            guess = mimetypes.guess_type(path)[0] or MimeTypes.File

        return guess
