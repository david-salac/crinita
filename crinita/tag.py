from typing import Any
import json
import datetime
from dataclasses import dataclass

from .utils import Utils
from .config import Config


@dataclass
class Tag(object):
    """Represents single tag in the system.

    Attributes:
        name (str): Name of the tag (e. g. Big Data)
        url_alias (str): Alias to the name (e. g. big-data)
    """
    name: str
    url_alias: str

    @property
    def url_alias_with_prefix(self):
        """Return URL alias with prefix"""
        return Config.tag_url_prefix + self.url_alias

    @property
    def url(self) -> str:
        """Link for the page defining tag"""
        return Utils.generate_file_path(self.url_alias_with_prefix)

    def __hash__(self):
        return self.url_alias.__hash__()

    def keys(self) -> list[str]:
        """Get keys that allows conversion of this class to dictionary.

        Returns:
            list[str]: List of the keys.
        """
        return ['name', 'url_alias']

    def __getitem__(self, key):
        """Allows conversion of this class to dictionary.
        """
        return getattr(self, key)


class JSONEncoderWithTags(json.JSONEncoder):
    """Allow to serialize tags"""
    def default(self, o: Any) -> Any:
        if isinstance(o, Tag):
            return dict(o)
        elif isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        return super().default(o)
