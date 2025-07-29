import os
import tempfile
import requests

class FileHandler:
    def __init__(self):
        pass

    def download_url_to_local(self, url: str) -> str:
        """Download a file from a URL to a local temp file and return the local path."""
        # Try to get extension from URL or Content-Type header
        ext = ""
        r = requests.head(url, allow_redirects=True)
        content_type = r.headers.get('content-type', '')
        if 'video/' in content_type or 'audio/' in content_type or 'image/' in content_type:
            ext = f".{content_type.split('/')[-1].split(';')[0]}"
        else:
            ext = os.path.splitext(url)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            r = requests.get(url, stream=True)
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=8192):
                tmp.write(chunk)
            return tmp.name