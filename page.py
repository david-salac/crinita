from typing import Optional, List

from jinja2 import Environment, FileSystemLoader

from .entity import Entity
from .config import Config


class Page(Entity):
    """Represents the single blog post.

    Attributes:
        large_image_path (Optional[str]): Path to the large image (background
            one).
        content (str): Content of the article.
        menu_position (Optional[int]): Position of the page in the menu.
                If None, page is not listed in menu.
    """

    def __init__(
        self,
        title: str,
        url_alias: str,
        large_image_path: Optional[str],
        content: str,
        menu_position: Optional[int] = None,
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
            large_image_path (str): Path to the large image (background one).
            content (str): Content of the article.
            menu_position (Optional[int]): Position of the page in the menu.
                If None, page is not listed in menu.
        """
        if template == "__DEFAULT__":
            template = Config.default_page_template

        # Call the entity constructor to pass meta tags
        super().__init__(template, title, description, keywords, url_alias)

        self.url_list = [url_alias]

        self.large_image_path: str = large_image_path
        self.content: str = content
        self.menu_position: Optional[int] = menu_position

    def keys(self) -> List[str]:
        """Get keys that allows conversion of this class to dictionary.

        Returns:
            List[str]: List of the keys to be passed to template.
        """
        return ['title', 'large_image_path', 'content']

    def __getitem__(self, key):
        """Allows conversion of this class to dictionary.
        """
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
