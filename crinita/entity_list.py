from typing import Optional, Any
import math

from jinja2 import Environment, FileSystemLoader

from .entity import Entity
from .config import Config
from .entity_detail import EntityDetail
from .utils import Utils


class EntityList(Entity):
    """Generate the list of entities with pagination.

    Attributes:
        template (str): Template that is used for the content generation.
        description (Optional[str]): Description of the page (meta tag).
        list_of_entities (list[EntityDetail]): List of all entities to be
            considered for pagination.
        number_of_pages (int): Number of pages in the pagination.
    """

    def __init__(
        self,
        title: str,
        list_of_entities: list[EntityDetail],
        url_alias: Optional[str] = None,
        template: str = '__DEFAULT__',
        description: Optional[str] = None,
        keywords: Optional[str] = None,
        template_parameters: dict[str, Any] = None
    ):
        """Create the new blog post.

        Args:
            template (str): Template that is used for the content generation.
            description (Optional[str]): Description of the page (meta tag).
            keywords (Optional[str]): Keywords of the page (meta tag), if None
                values for tags are used.
            url_alias (Optional[str]): Alias for the page (like my-page).
            list_of_entities (list[EntityDetail]): List of all entities to be
                considered for pagination.
            template_parameters (dict[str, Any]): All other additional
                parameters that are passed to the template engine.
        """
        # Call the entity constructor to pass meta tags
        super().__init__(template, title, description, keywords, url_alias,
                         template_parameters=template_parameters)

        self.list_of_entities: list[EntityDetail] = list_of_entities
        self._set_url_list()  # set-up self.url_list

    def _set_url_list(self) -> None:
        """Set-up the attribute self.url_list (called from constructor)
        """
        # Add itself (root page - if None = homepage)
        self.url_list = [self.url_alias]
        # Set up number of pages for the pagination
        self.number_of_pages: int = math.ceil(
            len(self.list_of_entities) / Config.pagination_max_item_per_page
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

    def generate_entities(self, page_position: int) -> dict:
        """Generate the content of the page (to template).

        Args:
             page_position (int): Relative position of the page in pagination
                indexed from 0.

        Returns:
            dict: keywords and values for template.
        """
        # Slice the entities (pagination)
        selection: list[EntityDetail] = self.list_of_entities[
            page_position * Config.pagination_max_item_per_page:
            min((page_position + 1) * Config.pagination_max_item_per_page,
                len(self.list_of_entities))
                    ]
        return {
            'entities': selection,
            'entities_length': len(selection),
            'page_position': page_position
        }

    def generate_pagination_nav_bar(self, page_position: int) -> dict:
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

    def generate_page(self,
                      url: str,
                      additional_tags: Optional[dict[str, Any]] = None) -> str:
        with Config.templates_path.joinpath(self.template).open() as tem_han:
            # Create template specific parameters
            template_parameters = Config.global_template_parameters | \
                                  self.template_parameters

            template = Environment(
                loader=FileSystemLoader(Config.templates_path)
            ).from_string(tem_han.read())
            # Page position in pagination (indexed from 0)
            page_position: int = self.url_list.index(url)
            html_str = template.render(
                {
                    **self.generate_pagination_nav_bar(page_position),
                    **self.generate_entities(page_position),
                    **template_parameters
                },
                additional_tags=(additional_tags if additional_tags else {})
            )
            return html_str
