from typing import Optional

from .config import Config


class Utils(object):
    @staticmethod
    def generate_file_path(url_root: Optional[str],
                           to_html_file: bool = False) -> str:
        """Generate the file name to the link on the page.
        Args:
            url_root (str): URL alias (None for homepage).
            to_html_file (bool): If True, the link to file is generated,
                if False, the URL link is generated.
        """
        if url_root is None:
            if to_html_file:
                return Config.site_home_file_name
            else:
                return Config.site_home_url
        return url_root + Config.site_file_suffix
