from typing import Optional, Any
import datetime
from pathlib import Path

from .entity_detail import EntityDetail
from .config import Config
from .tag import Tag, JSONEncoderWithTags


class Article(EntityDetail):
    """Represents a single blog post.

    Attributes:
        large_image_path (str): Path to the large image (background one).
        small_image_path (str): Path to the small image (icon).
        date (datetime.datetime): Date when article was published.
        lead (str): Lead of the article.
        content (str): Content of the article.
        tags (list[Tag]): Tags related to the article.
    """
    JSON_ENCODER = JSONEncoderWithTags

    def __init__(
        self,
        title: str,
        url_alias: str,
        date: datetime.datetime,
        lead: str,
        content: str,
        tags: list[Tag] = tuple(),
        large_image_path: Optional[str | Path] = None,
        small_image_path: Optional[str | Path] = None,
        template: str = '__DEFAULT__',
        description: Optional[str] = None,
        keywords: Optional[str] = None,
        template_parameters: dict[str, Any] = None
    ):
        """Create the new blog post.

        Args:
            template (str): A name of the file with Jinja2 template.
                If __DEFAULT__, the default template from Config class is used.
            title (str): Name of the article.
            description (Optional[str]): Description of the page (applies
                in meta tag); If None, lead is used instead.
            keywords (Optional[str]): Keywords related to the page (meta tag);
                if None, tag names are used.
            url_alias (str): Alias for the page (like my-page).
            tags (list[Tag]): List of tags of the article.

            large_image_path (Optional[str | Path]): Path to the large image
                (usually the background one).
            small_image_path (Optional[str | Path]): Path to the small image
                (usually the icon).
            date (datetime.datetime): Date when article was published.
            lead (str): Lead of the article.
            content (str): Content of the article.
            template_parameters (dict[str, Any]): All other additional
                parameters that are passed to the template engine.
        """
        if template == "__DEFAULT__":
            template = Config.default_article_template

        # Call the entity constructor to pass meta tags
        if keywords is None and len(tags) > 0:
            keywords = ", ".join([single_tag.name for single_tag in tags])

        super().__init__(template, title, description, keywords, url_alias,
                         template_parameters=template_parameters)

        self.tags: list[Tag] = tags

        self.large_image_path: Optional[str] = (str(large_image_path)
                                                if large_image_path else None)
        self.small_image_path: Optional[str] = (str(small_image_path)
                                                if small_image_path else None)
        self.date: datetime.datetime = date
        self.lead: str = lead
        self.content: str = content

    def keys(self) -> list[str]:
        """Get keys that allows conversion of this class to dictionary.

        Returns:
            list[str]: List of the keys to be passed to template.
        """
        return ['tags', 'title', 'small_image_path', 'large_image_path',
                'date', 'lead', 'content']

    def __getitem__(self, key):
        """Allows conversion of this class to dictionary.
        """
        if key == 'date':
            return self.date.strftime(Config.time_format)
        return getattr(self, key)
