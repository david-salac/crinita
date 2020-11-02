from typing import Optional, List
import datetime
from dataclasses import dataclass

from jinja2 import Environment, FileSystemLoader

from .entity import Entity
from .config import Config
from .utils import Utils


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


class Article(Entity):
    """Represents the single blog post.

    Attributes:
        large_image_path (str): Path to the large image (background one).
        small_image_path (str): Path to the small image (icon).
        date (datetime.datetime): Date when article was published.
        lead (str): Lead of the article.
        content (str): Content of the article.
        tags (List[Tag]): Tags related to the article.
    """

    def __init__(
        self,
        title: str,
        url_alias: str,
        large_image_path: str,
        small_image_path: str,
        date: datetime.datetime,
        lead: str,
        content: str,
        tags: List[Tag] = [],
        template: str = '__DEFAULT__',
        description: Optional[str] = None,
        keywords: Optional[str] = None
    ):
        """Create the new blog post.

        Args:
            template (str): Template that is used for the content generation.
            title (str): Name of the article.
            description (Optional[str]): Description of the page (meta tag).
            keywords (Optional[str]): Keywords of the page (meta tag), if None
                values for tags are used.
            url_alias (str): Alias for the page (like my-page).
            tags (List[Tag]): List of tags of the article.

            large_image_path (str): Path to the large image (background one).
            small_image_path (str): Path to the small image (icon).
            date (datetime.datetime): Date when article was published.
            lead (str): Lead of the article.
            content (str): Content of the article.
        """
        if template == "__DEFAULT__":
            template = Config.default_article_template
        # Call the entity constructor to pass meta tags
        if keywords is None and len(tags) > 0:
            keywords = ", ".join([single_tag.name for single_tag in tags])

        super().__init__(template, title, description, keywords, url_alias)

        self.tags: List[Tag] = tags
        self.url_list = [url_alias]

        self.large_image_path: str = large_image_path
        self.small_image_path: str = small_image_path
        self.date: datetime.datetime = date
        self.lead: str = lead
        self.content: str = content

    def keys(self) -> List[str]:
        """Get keys that allows conversion of this class to dictionary.

        Returns:
            List[str]: List of the keys to be passed to template.
        """
        return ['tags', 'title', 'large_image_path', 'date', 'lead', 'content']

    def __getitem__(self, key):
        """Allows conversion of this class to dictionary.
        """
        if key == 'date':
            return self.date.strftime(Config.time_format)
        return getattr(self, key)

    def generate_page(self, url: str) -> str:
        with open(Config.templates_path.joinpath(self.template)) as tem_han:
            template = Environment(
                loader=FileSystemLoader(Config.templates_path)
            ).from_string(tem_han.read())
            html_str = template.render(
                **dict(self)
            )
            return html_str
