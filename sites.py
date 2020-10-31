from typing import List, Dict, TYPE_CHECKING, Set
from pathlib import Path
from collections import defaultdict

from jinja2 import Environment, FileSystemLoader

from .config import Config

if TYPE_CHECKING:
    from .article import Article, Tag
    from .page import Page


class Sites(object):
    """Configuration of the sites

    Attributes:
        _list_of_articles: List of all articles ordered by date of publishing
            (from newest to oldest).
        _list_of_pages: List of all pages ordered by the position in menu.
        _tag_to_incidence: List of tag in the system (ordered by incidence from
            maximal to minimal).
        _tag_to_articles: Mapping from tag to list of articles.

        tag_cloud_template (str): Template file for the tag cloud.
        menu_template (str): Template file for the menu.
        recent_posts_template (str): Template file for the recent posts.
    """

    def __init__(
        self,
        list_of_articles: List['Article'],
        list_of_pages: List['Page'], *,
        check_url_unique: bool = True,
        tag_cloud_template: str = "__DEFAULT__",
        menu_template: str = "__DEFAULT__",
        recent_posts_template: str = "__DEFAULT__",
        text_sections_in_right_menu_template: str = "__DEFAULT__",
    ):
        """Create a new sites

        Args:
             list_of_pages (List['Page']): List of all pages to be included.
             list_of_articles (List['Article']): List of all articles to be
                included.
             check_url_unique (bool): If True, uniqueness of URLs is checked.
             tag_cloud_template (str): Template file for the tag cloud.
             menu_template (str): Template file for the menu.
             recent_posts_template (str): Template file for the recent posts.
             text_sections_in_right_menu_template (str): Template for the text
                section in right menu.
        """
        self.tag_cloud_template: str = tag_cloud_template
        self.menu_template: str = menu_template
        self.recent_posts_template: str = recent_posts_template
        self.text_sections_in_right_menu_template = \
            text_sections_in_right_menu_template

        if check_url_unique:
            # For sanity check (uniqueness of URLs)
            all_urls: Set[str] = set([])
            number_of_elements: int = 0
        # Process articles
        self._list_of_articles: List['Article'] = sorted(list_of_articles,
                                                         key=lambda x: x.date)
        self._tag_to_articles: Dict['Tag', List['Article']] = defaultdict(list)
        self._tag_to_incidence: Dict['Tag', int] = defaultdict(int)
        for article in list_of_articles:
            if check_url_unique:
                # Add url to set (for sanity check)
                all_urls.add(article.url_alias)
                number_of_elements += 1
            # Handle tags
            for tag in article.tags:
                self._tag_to_articles[tag].append(article)
                self._tag_to_incidence[tag] += 1
        # Sort dictionary by values from the biggest to lowest
        self._tag_to_incidence = {
            k: v for k, v in sorted(self._tag_to_incidence.items(),
                                    key=lambda item: item[1],
                                    reverse=True)
        }
        # Process pages
        self._list_of_pages: List['Page'] = sorted(
            list_of_pages,
            key=lambda x: x.menu_position if x.menu_position else -1
        )
        if check_url_unique:
            for page in list_of_pages:
                all_urls.add(page.url_alias)
                number_of_elements += 1

            # Proceed the sanity check:
            if len(all_urls) != number_of_elements:
                raise ValueError("Not all URLs are unique!")

    def generate_tag_cloud(self) -> str:
        """Generate the tag cloud.

        Returns:
            str: HTML code for the tag cloud.
        """
        template = self.tag_cloud_template
        if template == "__DEFAULT__":
            template = Config.default_tag_cloud_template
        # Generate HTML code
        with open(Config.templates_path.joinpath(template)) as tem_han:
            template = Environment(
                loader=FileSystemLoader(Config.templates_path)
            ).from_string(tem_han.read())
            html_str = template.render(
                tags=self.list_of_tags[:min(Config.maximal_tag_cloud_size,
                                            len(self.list_of_tags))]
            )
            return html_str

    def generate_menu(self) -> str:
        """Generate the menu.

        Returns:
            str: HTML code for the menu.
        """
        template = self.menu_template
        if template == "__DEFAULT__":
            template = Config.default_menu_template
        # Generate HTML code
        with open(Config.templates_path.joinpath(template)) as tem_han:
            template = Environment(
                loader=FileSystemLoader(Config.templates_path)
            ).from_string(tem_han.read())
            html_str = template.render(
                menu_items=self.list_of_pages_in_menu
            )
            return html_str

    def generate_recent_posts(self) -> str:
        """Generate the recent posts tag.

        Returns:
            str: HTML code for the recent posts tag.
        """
        template = self.recent_posts_template
        if template == "__DEFAULT__":
            template = Config.default_recent_posts
        # Generate HTML code
        with open(Config.templates_path.joinpath(template)) as tem_han:
            template = Environment(
                loader=FileSystemLoader(Config.templates_path)
            ).from_string(tem_han.read())
            html_str = template.render(
                recent_posts=self.list_of_articles[:min(
                    len(self.list_of_articles), Config.maximal_recent_posts
                )]
            )
            return html_str

    def generate_text_sections_in_right_menu(self) -> str:
        """Generate the text sections in right menu.

        Returns:
            str: HTML code for the right menu text section.
        """
        template = self.text_sections_in_right_menu_template
        if template == "__DEFAULT__":
            template = Config.default_text_sections_in_right_menu_template
        # Generate HTML code
        with open(Config.templates_path.joinpath(template)) as tem_han:
            template = Environment(
                loader=FileSystemLoader(Config.templates_path)
            ).from_string(tem_han.read())
            right_menu_text = ""
            for item in Config.text_sections_in_right_menu:
                right_menu_text += template.render(**item)
            return right_menu_text

    def generate_page(
        self,
        output_directory_path: Path
    ):
        # TODO
        pass

    @property
    def list_of_articles(self):  # Ordered by date
        return self._list_of_articles

    @property
    def list_of_pages(self):  # Ordered by date
        return self._list_of_pages

    @property
    def list_of_pages_in_menu(self):  # Ordered by date
        for i in range(len(self._list_of_pages)):
            if self._list_of_pages[i].menu_position is not None:
                return self._list_of_pages[i:]
        return []

    @property
    def list_of_tags(self):  # Ordered by incidence
        return list(self._tag_to_incidence.keys())

    @property
    def tags_with_incidences(self):  # Ordered by incidence
        return self._tag_to_incidence

    @property
    def tag_to_articles(self):  # Ordered by date
        return self._tag_to_articles
