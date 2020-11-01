from typing import Optional, List
import math

from jinja2 import Environment, FileSystemLoader

from .entity import Entity
from .config import Config
from .article import Tag, Article
from .utils import Utils


class ListOfArticles(Entity):
    """Generate the list of articles with pagination.

    Attributes:
        template (str): Template that is used for the content generation.
        description (Optional[str]): Description of the page (meta tag).
        tag (Optional[Tag]): Tag that is the subject of filtration. If None
            all tags are considered.
        list_of_articles (List[Article]): List of all articles to be
            considered for pagination.
        number_of_pages (int): Number of pages in the pagination.
    """

    def __init__(
        self,
        list_of_articles: List[Article],
        url_alias: Optional[str] = None,
        tag: Optional[Tag] = None,
        template: str = '__DEFAULT__',
        description: Optional[str] = None,
        keywords: Optional[str] = None
    ):
        """Create the new blog post.

        Args:
            template (str): Template that is used for the content generation.
            description (Optional[str]): Description of the page (meta tag).
            keywords (Optional[str]): Keywords of the page (meta tag), if None
                values for tags are used.
            url_alias (Optional[str]): Alias for the page (like my-page).
            tag (Optional[Tag]): Tag that is the subject of filtration. If None
                all tags are considered.
            list_of_articles (List[Article]): List of all articles to be
                considered for pagination.
        """
        if template == "__DEFAULT__":
            template = Config.default_article_list_template
        # Construct the page title (prefer tag, if not set up, set to None)
        title: str = None
        if tag:
            title = tag.name
        # Call the entity constructor to pass meta tags
        super().__init__(template, title, description, keywords, url_alias)

        self.tag: Tag = tag
        self.list_of_articles: List[Article] = list_of_articles
        self._set_url_list()  # set-up self.url_list

    def _set_url_list(self) -> None:
        """Set-up the attribute self.url_list (called from constructor)
        """
        # Add itself (root page - if None = homepage)
        self.url_list = [self.url_alias]
        # Set up number of pages for the pagination
        self.number_of_pages: int = math.ceil(
            len(self.list_of_articles) / Config.pagination_max_item_per_page
        )
        # Set-up urls for each page in the pagination:
        root_of_pagination_url: str = Config.pagination_suffix
        if self.url_alias is not None:
            root_of_pagination_url = (self.url_alias +
                                      Config.pagination_prefix +
                                      root_of_pagination_url)
        # From 1 because the first page is already added
        for page_nr in range(1, self.number_of_pages):
            self.url_list.append(
                root_of_pagination_url + str(page_nr)
            )

    def _generate_content(self, page_position: int) -> dict:
        """Generate the content of the page (to template).

        Args:
             page_position (int): Relative position of the page in pagination
                indexed from 0.

        Returns:
            dict: keywords and values for template.
        """
        # Slice the articles
        selection: List[Article] = self.list_of_articles[
            page_position * Config.pagination_max_item_per_page:
            min((page_position + 1) * Config.pagination_max_item_per_page,
                len(self.list_of_articles))
                    ]
        first_article = None
        if page_position == 0:
            # Use first article in the list separately (due to different style)
            first_article = selection[0]
            # Remove the first article from the list:
            selection = selection[1:]
        return {
            'first_preview': first_article,
            'article_previews': selection
        }

    def _generate_pagination_nav_bar(self, page_position: int) -> dict:
        """Generate the pagination navigation bar (link to next and previous
            page).

        Args:
             page_position (int): Relative position of the page in pagination
                indexed from 0.

        Returns:
            dict: keywords and values for template.
        """
        link_newer: str = None
        if page_position > 0:
            link_newer = Utils.generate_file_path(
                self.url_list[page_position - 1]
            )
        link_older: str = None
        if page_position < (len(self.url_list) - 1):
            link_older = Utils.generate_file_path(
                self.url_list[page_position + 1]
            )
        return {
            'navigation_previous': link_older,
            'navigation_next': link_newer
        }

    def generate_page(self, url: str) -> str:
        with Config.templates_path.joinpath(self.template).open() as tem_han:
            template = Environment(
                loader=FileSystemLoader(Config.templates_path)
            ).from_string(tem_han.read())
            # Page position in pagination (indexed from 0)
            page_position: int = self.url_list.index(url)
            html_str = template.render(
                {
                    **self._generate_pagination_nav_bar(page_position),
                    **self._generate_content(page_position)
                }
            )
            return html_str
