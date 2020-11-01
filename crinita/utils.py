from typing import Optional

from .config import Config


class Utils(object):
    @staticmethod
    def generate_file_path(url_root: Optional[str]) -> str:
        """Generate the file name to the link on the page.
        """
        if url_root is None:
            return Config.site_home_file_name
        return url_root + Config.site_file_suffix
