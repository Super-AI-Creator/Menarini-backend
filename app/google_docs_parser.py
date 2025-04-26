from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials

def authenticate_service_account(service_account_file, scopes):
    """
    Authenticate using a service account and return the service object.
    """
    creds = Credentials.from_service_account_file(service_account_file, scopes=scopes)
    service = build('docs', 'v1', credentials=creds)
    return service

def parse_google_doc(doc_url, service_account_file):
    """
    Parses the content of a Google Docs document and returns its text.

    :param doc_url: The URL of the Google Docs document.
    :param service_account_file: Path to the service account JSON credentials file.
    :return: Text content of the document.
    """
    # Define the API scope needed for the Docs API
    SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

    try:
        service = authenticate_service_account(service_account_file, SCOPES)
    except Exception as e:
        print(f"Error authenticating service account: {e}")
        return None


    doc_id = doc_url.split("/")[-2]

    try:

        doc = service.documents().get(documentId=doc_id).execute()

        content = doc.get("body", {}).get("content", [])
        doc_text = []

        for element in content:
            if 'paragraph' in element:
                for para_element in element['paragraph'].get('elements', []):
                    if 'textRun' in para_element:
                        doc_text.append(para_element['textRun']['content'])

        return "\n".join(doc_text)

    except HttpError as error:
        print(f"An error occurred while fetching the document: {error}")
        return None
