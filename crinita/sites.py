import json
import copy
import datetime
from typing import Optional
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
import shutil
import tempfile

from jinja2 import Environment, FileSystemLoader

from .config import Config
from .utils import Utils
from .article import Article
from .tag import Tag
from .dataset import Dataset
from .entity import Entity
from .page import Page
from .list_of_articles import ListOfArticles
from .entity_list import EntityList
from .entity_detail import EntityDetail
from .list_of_datasets import ListOfDatasets
from .dataset import DataEntity


@dataclass()
class _SinglePageHTML(object):
    """Dataclass for generation of the HTML page from layout.
    """
    title: str
    menu: str
    page_content: str
    recent_posts: str
    recent_datasets: str
    article_tag_cloud: str
    dataset_tag_cloud: str
    text_section_in_right_menu: str
    page_name: Optional[str] = None,
    meta_description: str = None
    meta_keywords: str = None
    meta_author: str = None
    append_to_head_tag: str = None
    homepage_link: str = None
    site_logo_text: str = None
    footer: str = None
    # Additional template parameters (defined by entity and global
    template_parameters: Optional[dict[str, object]] = None
    # Path to CSS file
    css_style_path: str = None

    def keys(self) -> list[str]:
        """Get keys that allows conversion of this class to dictionary.

        Returns:
            list[str]: List of the keys to be passed to template.
        """
        return [atr for atr in vars(self) if '__' not in atr]

    def __getitem__(self, key):
        """Allows conversion of this class to dictionary.
        """
        return getattr(self, key)

    def write_to_file(
        self,
        file_path: Path | str,
        layout_template_path: Path | str
    ) -> None:
        """Write page content to the HTML file.

        Args:
            file_path (Path | str): Path to the file
            layout_template_path (Path | str): Path to the layout template
        """
        if type(file_path) == str:
            file_path = Path(file_path)
        if type(layout_template_path) == str:
            layout_template_path = Path(layout_template_path)

        if self.meta_description is None:
            self.meta_description = Config.default_meta_description
        if self.meta_keywords is None:
            self.meta_keywords = Config.default_meta_keywords
        if self.meta_author is None:
            self.meta_author = Config.default_meta_meta_author
        if self.append_to_head_tag is None:
            self.append_to_head_tag = Config.append_to_head_tag
        if self.footer is None:
            self.footer = Config.footer
        if self.site_logo_text is None:
            self.site_logo_text = Config.site_logo_text
        if self.homepage_link is None:
            self.homepage_link = Config.site_home_url
        if self.css_style_path is None and Config.css_style_path:
            self.css_style_path = Config.css_style_path.name

        with Config.templates_path.joinpath(
            layout_template_path
        ).open('r') as html_template:
            template = Environment(
                loader=FileSystemLoader(Config.templates_path)
            ).from_string(html_template.read())

            html_str = template.render(**dict(self))
            with file_path.open('w') as writer_to_html:
                writer_to_html.write(html_str)


class Sites(object):
    """Configuration of the sites

    Attributes:
        _list_of_articles: List of all articles ordered by date of publishing
            (from newest to oldest).
        _list_of_pages: List of all pages ordered by the position in menu.
        _tag_to_articles_incidence: List of tag in the system (ordered by
            incidence from maximal to minimal).
        _tag_to_articles: Mapping from tag to list of articles.
        article_tag_cloud_template (str): Template file for the article's tag
            cloud.
        dataset_tag_cloud_template (str): Template file for the dataset's tag
            cloud.
        menu_template (str): Template file for the menu.
        recent_posts_template (str): Template file for the recent posts.
        _site_map_urls (list[str]): List of all URLs in the app
        _homepage (Entity): Entity that represents homepage
    """
    # Define JSON encoder for the object
    JSON_ENCODER = json.JSONEncoder

    def __init__(
        self,
        list_of_entities: list[Article | Page | Dataset], *,
        check_url_unique: bool = True,
        layout_template: str | Path = "__DEFAULT__",
        article_tag_cloud_template: str = "__DEFAULT__",
        dataset_tag_cloud_template: str = "__DEFAULT__",
        menu_template: str = "__DEFAULT__",
        recent_posts_template: str = "__DEFAULT__",
        recent_datasets_template: str = "__DEFAULT__",
        text_sections_in_right_menu_template: str = "__DEFAULT__"
    ):
        """Create a new sites

        Args:
            list_of_entities (list[Article | Page]): List of all pages
               and articles to be included.
            check_url_unique (bool): If True, uniqueness of URLs is checked.
            layout_template (str | Path): Template file for the whole sites.
            article_tag_cloud_template (str): Template file for the article's
                tag cloud.
            dataset_tag_cloud_template (str): Template file for the dataset's
                tag cloud.
            menu_template (str): Template file for the menu.
            recent_posts_template (str): Template file for recent posts.
            recent_datasets_template (str): Template file for recent datasets.
            text_sections_in_right_menu_template (str): Template for the text
               section in right menu.
        """
        # Separate Page, Datasets and Article instances from all entities
        list_of_articles: list[Article] = [
            ent for ent in list_of_entities if isinstance(ent, Article)
        ]
        list_of_datasets: list[Dataset] = [
            ent for ent in list_of_entities if isinstance(ent, Dataset)
        ]
        list_of_pages: list[Page] = [
            ent for ent in list_of_entities if isinstance(ent, Page)
        ]

        self.article_tag_cloud_template: str = article_tag_cloud_template
        self.dataset_tag_cloud_template: str = dataset_tag_cloud_template
        self.menu_template: str = menu_template
        self.recent_posts_template: str = recent_posts_template
        self.recent_datasets_template: str = recent_datasets_template
        self.text_sections_in_right_menu_template: str = \
            text_sections_in_right_menu_template
        self.layout_template: str | Path = layout_template

        # For checking of URL uniqueness
        all_urls: set[str] = set([])
        number_of_elements: int = 0

        # Process articles
        self._list_of_articles: list[Article] = sorted(list_of_articles,
                                                       key=lambda x: x.date,
                                                       reverse=True)
        _article_tag_to_articles, _article_tag_to_incidence, _articles_urls = \
            self._process_entity_list(self._list_of_articles)
        self._tag_to_articles = _article_tag_to_articles
        self._tag_to_articles_incidence = _article_tag_to_incidence
        if check_url_unique:
            all_urls |= set(_articles_urls)
            number_of_elements += len(_articles_urls)

        # Process datasets
        self._list_of_datasets: list[Dataset] = sorted(list_of_datasets,
                                                       key=lambda x: x.date,
                                                       reverse=True)
        _dataset_tag_to_articles, _dataset_tag_to_incidence, _dataset_urls = \
            self._process_entity_list(self._list_of_datasets)
        self._tag_to_datasets = _dataset_tag_to_articles
        self._tag_to_datasets_incidence = _dataset_tag_to_incidence
        if check_url_unique:
            all_urls |= set(_dataset_urls)
            number_of_elements += len(_dataset_urls)

        # Process pages
        self._list_of_pages: list[Page] = sorted(
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

        self._site_map_urls: list[str] = []
        self._homepage: Entity = None

    @staticmethod
    def _process_entity_list(
        list_of_entities: list[Dataset | Article]) -> tuple[
            dict[Tag, list[EntityDetail]], dict[Tag, int], list[str]
    ]:
        """Initiate entity list
        Args:
            list_of_entities (list[Dataset | Article]): List of entities
                that are processed.
        Returns:
            tuple[dict[Tag, list[EntityDetail]], dict[Tag, int], list[str]]:
                first entity is mapping from tag to ordered list of entities,
                second is mapping from tag to count of entities,
                third is the list of all URLs
        """

        _tag_to_entity: dict[Tag, list[EntityDetail]] = defaultdict(list)
        _tag_to_entity_incidence: dict[Tag, int] = defaultdict(int)
        _all_urls: list[str] = list()
        for entity in list_of_entities:
            # Add url to set (for sanity check)
            _all_urls.append(entity.url_alias)

            # Handle tags
            for tag in entity.tags:
                _tag_to_entity[tag].append(entity)
                _tag_to_entity_incidence[tag] += 1

        # Sort articles in tag by date of publishing
        for tag in _tag_to_entity.keys():
            _tag_to_entity[tag] = sorted(_tag_to_entity[tag],
                                         key=lambda x: x.date,
                                         reverse=True)
        # Sort dictionary by values from the biggest to lowest
        _tag_to_entity_incidence = {
            k: v for k, v in sorted(_tag_to_entity_incidence.items(),
                                    key=lambda item: item[1],
                                    reverse=True)
        }
        return _tag_to_entity, _tag_to_entity_incidence, _all_urls

    @lru_cache()
    def generate_article_tag_cloud(self) -> str:
        """Generate the article's tag cloud.

        Returns:
            str: HTML code for the tag cloud.
        """
        template = self.article_tag_cloud_template
        if template == "__DEFAULT__":
            template = Config.default_article_tag_cloud_template
        # Generate HTML code
        with open(Config.templates_path.joinpath(template)) as tem_han:
            template = Environment(
                loader=FileSystemLoader(Config.templates_path)
            ).from_string(tem_han.read())
            html_str = template.render(
                tags=self.list_article_tags[
                     :min(Config.maximal_article_tag_cloud_size,
                          len(self.list_article_tags))
                     ],
                tag_cloud_title=Config.title_article_tag_cloud
            )
            return html_str

    @lru_cache()
    def generate_dataset_tag_cloud(self) -> str:
        """Generate the dataset's tag cloud.

        Returns:
            str: HTML code for the dataset's tag cloud.
        """
        template = self.dataset_tag_cloud_template
        if template == "__DEFAULT__":
            template = Config.default_dataset_tag_cloud_template
        # Generate HTML code
        with open(Config.templates_path.joinpath(template)) as tem_han:
            template = Environment(
                loader=FileSystemLoader(Config.templates_path)
            ).from_string(tem_han.read())
            html_str = template.render(
                tags=self.list_dataset_tags[
                     :min(Config.maximal_dataset_tag_cloud_size,
                          len(self.list_dataset_tags))
                     ],
                tag_cloud_title=Config.title_dataset_tag_cloud
            )
            return html_str

    @lru_cache()
    def generate_menu(self) -> str:
        """Generate the menu.

        Returns:
            str: HTML code for the menu.
        """
        template = self.menu_template
        if template == "__DEFAULT__":
            template = Config.default_menu_template

        # Load external menu items
        @dataclass()
        class _MenuItem(object):
            url: str
            title: str
            menu_position: int
        external_items = []  # External menu items
        for external_item in Config.append_to_menu:
            item = _MenuItem(external_item['url'],
                             external_item['title'],
                             external_item['menu_position'])
            if item.url == "__HOME_PAGE__":
                item.url = Config.site_home_url
            if item.url == "__BLOG__":
                item.url = Utils.generate_file_path(Config.blog_url)
            if item.url == "__DATASET__":
                item.url = Utils.generate_file_path(Config.dataset_url)
            external_items.append(item)
        all_items_in_menu: list = self.list_of_pages_in_menu + external_items

        # Sort all items by the position inside the menu
        all_items_in_menu.sort(key=lambda x: x.menu_position)

        # Generate HTML code
        with open(Config.templates_path.joinpath(template)) as tem_han:
            template = Environment(
                loader=FileSystemLoader(Config.templates_path)
            ).from_string(tem_han.read())
            html_str = template.render(
                menu_items=all_items_in_menu
            )
            return html_str

    @lru_cache()
    def generate_recent_posts(self) -> str:
        """Generate the recent posts tag.

        Returns:
            str: HTML code for the recent posts tag.
        """
        template = self.recent_posts_template
        if template == "__DEFAULT__":
            template = Config.default_recent_posts_template
        # Generate HTML code
        with open(Config.templates_path.joinpath(template)) as tem_han:
            template = Environment(
                loader=FileSystemLoader(Config.templates_path)
            ).from_string(tem_han.read())
            html_str = template.render(
                recent_elements=self.list_of_articles[:min(
                    len(self.list_of_articles), Config.maximal_recent_posts
                )],
                recent_elements_title=Config.recent_posts_title
            )
            return html_str

    @lru_cache()
    def generate_recent_datasets(self) -> str:
        """Generate the recent datasets tag.

        Returns:
            str: HTML code for the recent datasets tag.
        """
        template = self.recent_datasets_template
        if template == "__DEFAULT__":
            template = Config.default_recent_datasets_template
        # Generate HTML code
        with open(Config.templates_path.joinpath(template)) as tem_han:
            template = Environment(
                loader=FileSystemLoader(Config.templates_path)
            ).from_string(tem_han.read())
            html_str = template.render(
                recent_elements=self.list_of_datasets[:min(
                    len(self.list_of_datasets), Config.maximal_recent_datasets
                )],
                recent_elements_title=Config.recent_datasets_title
            )
            return html_str

    @lru_cache()
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

    def _generate_entity(
        self,
        page_entity: Article | Dataset | Page,
        output_directory_path: Path,
        rewrite_if_exists: bool
    ) -> None:
        """Generate HTML code and save it to the file for an article or page.

        Args:
            output_directory_path (Path): Path where the output files are
                generated.
            rewrite_if_exists (bool): If True, files are rewritten; if False,
                exception is raised.
        """
        target_file: Path = Path(
            output_directory_path, Utils.generate_file_path(
                page_entity.url_alias, True
            )
        )
        if not rewrite_if_exists and target_file.exists():
            # Skip if existing files must not be rewritten.
            raise FileExistsError("this file already exists")
        # Parse layout template
        if self.layout_template == "__DEFAULT__":
            layout_template = Config.default_layout_template
        else:
            layout_template = self.layout_template

        # Write content to file
        _SinglePageHTML(
            page_content=page_entity.generate_page(
                page_entity.url_alias,
                additional_tags={
                    'article_tag_cloud': self.generate_article_tag_cloud(),
                    'recent_posts': self.generate_recent_posts(),
                    'dataset_tag_cloud': self.generate_dataset_tag_cloud(),
                    'recent_datasets': self.generate_recent_datasets(),
                }
            ),
            title=page_entity.page_title,
            page_name=page_entity.page_name,
            # Additional (optional) parameters merged with global version
            template_parameters=Config.global_template_parameters | \
                                page_entity.template_parameters,

            # Generate blocks
            meta_description=page_entity.description,
            meta_keywords=page_entity.keywords,
            menu=self.generate_menu(),
            recent_posts=self.generate_recent_posts(),
            recent_datasets=self.generate_recent_datasets(),
            article_tag_cloud=self.generate_article_tag_cloud(),
            dataset_tag_cloud=self.generate_dataset_tag_cloud(),
            text_section_in_right_menu=self.generate_text_sections_in_right_menu()  # noqa: E501
        ).write_to_file(target_file, layout_template)

        # Append to site map
        self._site_map_urls.append(page_entity.url)

    def _generate_list_of_entities_with_pagination(
        self,
        tag: Optional[Tag],
        output_directory_path: Path,
        rewrite_if_exists: bool,
        list_type: type[EntityList],
        *,
        list_page: Optional[EntityList] = None,
        tag_to_entities: Optional[dict[Tag, list[EntityDetail]]] = None
    ) -> None:
        """Generate all files related to the concrete tag in the system.

        Args:
            tag (Tag): Tag for that content is generated.
            output_directory_path (Path): Path where the output files are
                generated.
            rewrite_if_exists (bool): If True, files are rewritten; if False,
                exception is raised.
            list_type (type[EntityList]): Class defining entity list.
            list_page (Optional[ListOfArticles]): Entity that is used for
                pagination (if None, new entity is created from the tag).
            tag_to_entities (Optional[dict[Tag, list[EntityDetail]]]): Mapping
                from tag to concrete entities (ordered as wanted). Applies
                only if 'list_page' argument is None.
        """
        if list_page is None:
            list_page: list_type = list_type(
                title=tag.name,
                list_of_entities=tag_to_entities[tag],
                url_alias=tag.url_alias_with_prefix
            )
        # Parse layout template
        if self.layout_template == "__DEFAULT__":
            layout_template = Config.default_layout_template
        else:
            layout_template = self.layout_template

        for single_url in list_page.url_list:
            target_file: Path = Path(
                output_directory_path, Utils.generate_file_path(single_url,
                                                                True)
            )
            if not rewrite_if_exists and target_file.exists():
                # Skip if existing files must not be rewritten.
                raise FileExistsError("this file already exists")
            # Write content to file
            _SinglePageHTML(
                page_content=list_page.generate_page(
                    single_url,
                    additional_tags={
                        'article_tag_cloud': self.generate_article_tag_cloud(),
                        'recent_posts': self.generate_recent_posts(),
                        'dataset_tag_cloud': self.generate_dataset_tag_cloud(),
                        'recent_datasets': self.generate_recent_datasets(),
                    }
                ),
                title=list_page.page_title,
                page_name=list_page.page_name,

                # Generate blocks
                meta_description=list_page.description,
                meta_keywords=list_page.keywords,
                menu=self.generate_menu(),
                recent_posts=self.generate_recent_posts(),
                recent_datasets=self.generate_recent_datasets(),
                article_tag_cloud=self.generate_article_tag_cloud(),
                dataset_tag_cloud=self.generate_dataset_tag_cloud(),
                text_section_in_right_menu=self.generate_text_sections_in_right_menu()  # noqa: E501
            ).write_to_file(target_file, layout_template)

            # Append to site map
            self._site_map_urls.append(Utils.generate_file_path(single_url))

    def generate_pages(
        self,
        output_directory_path: Path,
        *,
        rewrite_if_exists: bool = True
    ) -> None:
        """
        Args:
            output_directory_path (Path): Path to the directory where outputs
                are generated.
            rewrite_if_exists (bool): If True, files are rewritten; if False,
                exception is raised.
        """
        # Create target directory
        if rewrite_if_exists:
            if not output_directory_path.exists():
                output_directory_path.mkdir()

        # Copy resources
        if Config.resources_path:
            shutil.copytree(Config.resources_path,
                            output_directory_path,
                            dirs_exist_ok=True)
        # Copy CSS style file
        if Config.css_style_path:
            shutil.copy2(
                Config.css_style_path,
                output_directory_path / Config.css_style_path.name
            )

        # Generate all articles
        for article in self.list_of_articles:
            self._generate_entity(
                page_entity=article,
                output_directory_path=output_directory_path,
                rewrite_if_exists=rewrite_if_exists
            )

        # Generate all datasets
        for dataset in self.list_of_datasets:
            self._generate_entity(
                page_entity=dataset,
                output_directory_path=output_directory_path,
                rewrite_if_exists=rewrite_if_exists
            )

        # Generate all pages related to pagination of articles
        if isinstance(self.homepage, ListOfArticles):
            self._generate_list_of_entities_with_pagination(
                tag=None,
                output_directory_path=output_directory_path,
                rewrite_if_exists=rewrite_if_exists,
                list_type=ListOfArticles,
                list_page=self.homepage,
                tag_to_entities=self.tag_to_articles
            )
        for tag in self.list_article_tags:
            self._generate_list_of_entities_with_pagination(
                tag=tag,
                output_directory_path=output_directory_path,
                list_type=ListOfArticles,
                rewrite_if_exists=rewrite_if_exists,
                tag_to_entities=self.tag_to_articles
            )
        if Config.blog_url:
            self._generate_list_of_entities_with_pagination(
                tag=None,
                output_directory_path=output_directory_path,
                list_type=ListOfArticles,
                rewrite_if_exists=rewrite_if_exists,
                list_page=self.generate_blog(Config.blog_title,
                                             Config.blog_url)
            )

        # Generate all pages related to pagination of datasets
        if isinstance(self.homepage, ListOfDatasets):
            self._generate_list_of_entities_with_pagination(
                tag=None,
                output_directory_path=output_directory_path,
                rewrite_if_exists=rewrite_if_exists,
                list_type=ListOfDatasets,
                list_page=self.homepage,
                tag_to_entities=self.tag_to_datasets
            )
        for tag in self.list_dataset_tags:
            self._generate_list_of_entities_with_pagination(
                tag=tag,
                output_directory_path=output_directory_path,
                list_type=ListOfDatasets,
                rewrite_if_exists=rewrite_if_exists,
                tag_to_entities=self.tag_to_datasets
            )
        if Config.dataset_url:
            self._generate_list_of_entities_with_pagination(
                tag=None,
                output_directory_path=output_directory_path,
                list_type=ListOfDatasets,
                rewrite_if_exists=rewrite_if_exists,
                list_page=self.generate_datasets(Config.dataset_title,
                                                 Config.dataset_url)
            )

        # Generate all pages
        for page in self.list_of_pages:
            self._generate_entity(
                page_entity=page,
                output_directory_path=output_directory_path,
                rewrite_if_exists=rewrite_if_exists
            )

        # Write site map file
        with output_directory_path.joinpath(
                'sitemap.xml').open('w') as site_map_handler:
            with Config.templates_path.joinpath(
                Config.site_map_template
            ).open('r') as sitemap_template:
                template = Environment(
                    loader=FileSystemLoader(Config.templates_path)
                ).from_string(sitemap_template.read())
                site_map_urls_with_prefix: list[str] = []
                for single_url in self._site_map_urls:
                    if single_url == '/':
                        # Causes troubles when merging routes
                        site_map_urls_with_prefix.append(
                            Config.site_map_url_prefix
                        )
                    else:
                        site_map_urls_with_prefix.append(
                            Config.site_map_url_prefix + single_url
                        )
                sitemap_def: str = template.render(
                    urls=site_map_urls_with_prefix
                )
                site_map_handler.write(sitemap_def)

        # Write robots.txt
        with output_directory_path.joinpath(
                'robots.txt').open('w') as robots_txt:
            robots_txt.write(Config.robots_txt)

    @property
    def list_of_articles(self):  # Ordered by date
        return self._list_of_articles

    @property
    def list_of_datasets(self):  # Ordered by date
        return self._list_of_datasets

    @property
    def list_of_pages(self):  # Ordered by date
        return self._list_of_pages

    @property
    @lru_cache()
    def list_of_pages_in_menu(self):  # Ordered by date
        for i in range(len(self._list_of_pages)):
            if self._list_of_pages[i].menu_position is not None:
                return self._list_of_pages[i:]
        return []

    @property
    def list_article_tags(self) -> list[Tag]:
        """List of tags related to article"""
        return list(self._tag_to_articles_incidence.keys())

    @property
    def list_dataset_tags(self) -> list[Tag]:
        """List of tags related to datasets"""
        return list(self._tag_to_datasets_incidence.keys())

    @property
    def article_tags_with_incidences(self) -> dict[Tag, int]:
        """Dictionary key is ordered by incidence"""
        return self._tag_to_articles_incidence

    @property
    def tag_to_articles(self):  # Ordered by date
        return self._tag_to_articles

    @property
    def tag_to_datasets(self):  # Ordered by date
        return self._tag_to_datasets

    @property
    @lru_cache()
    def homepage(self) -> Entity:
        """Get the homepage of the sites. Technically the Entity that has
            url_alias set to None. If there is not any Entity, the new one
            is created as a list of all articles in the system.
        """
        if self._homepage:
            return self._homepage

        # Run through all pages:
        homepage_ent: Entity = None
        for page in self.list_of_pages:
            if page.url_alias is None:
                if homepage_ent is not None:
                    raise ValueError("there are (at least) two homepages")
                homepage_ent = page

        # Run through all articles:
        for article in self.list_of_articles:
            if article.url_alias is None:
                if homepage_ent is not None:
                    raise ValueError("there are (at least) two homepages")
                homepage_ent = article

        # Run through all articles:
        for dataset in self.list_of_datasets:
            if dataset.url_alias is None:
                if homepage_ent is not None:
                    raise ValueError("there are (at least) two homepages")
                homepage_ent = dataset

        # If there is no explicit homepage, generate as a list of all articles
        if homepage_ent is None:
            homepage_ent = self.generate_blog(None, None)

        self._homepage = homepage_ent
        return homepage_ent

    @homepage.setter
    def homepage(self, value: Entity):
        """Set the homepage."""
        if value.url_alias is not None:
            raise AttributeError('url_alias has to be None value')
        self._homepage = value

    @lru_cache()
    def generate_blog(self,
                      title: Optional[str],
                      url_alias: Optional[str]) -> ListOfArticles:
        """Generate blog (list of articles without tag).
        Args:
            title (Optional[str]): Title of the page.
            url_alias (Optional[str]): URL prefix for page.
        Return:
            ListOfArticles: Blog articles.
        """
        return ListOfArticles(
            title=title,
            list_of_entities=self.list_of_articles,
            url_alias=url_alias
        )

    @lru_cache()
    def generate_datasets(self,
                          title: Optional[str],
                          url_alias: Optional[str]) -> ListOfDatasets:
        """Generate data catalogue (list of datasets without tag).
        Args:
            title (Optional[str]): Title of the page.
            url_alias (Optional[str]): URL prefix for page.
        Return:
            ListOfDatasets: Dataset entities.
        """
        return ListOfDatasets(
            title=title,
            list_of_entities=self.list_of_datasets,
            url_alias=url_alias
        )

    @staticmethod
    def object_from_json(json_def: str | dict) -> Entity:
        """Deserialize object (Page or Article) from JSON.

        Args:
            json_def (str): JSON string defining object or dictionary.

        Returns:
            Entity: Concrete object.
        """
        if isinstance(json_def, str):
            deserialized: dict = json.loads(json_def)
        else:
            deserialized: dict = copy.deepcopy(json_def)

        match deserialized.pop('object_type'):
            case Page.__name__:
                return Page(**deserialized)
            case Article.__name__:
                tags_def = deserialized.pop('tags')
                tags = []
                for tag_dict in tags_def:
                    tags.append(Tag(**tag_dict))
                    # Extract date:
                date = datetime.datetime.strptime(deserialized.pop('date'),
                                                  "%Y-%m-%dT%H:%M:%S")
                return Article(**deserialized, tags=tags, date=date)
            case Dataset.__name__:
                # Extract tags
                tags_def = deserialized.pop('tags')
                tags = []
                for tag_dict in tags_def:
                    tags.append(Tag(**tag_dict))
                # Extract data entities
                data_entities_def = deserialized.pop('data_entities')
                data_entities = []
                for data_entity_dict in data_entities_def:
                    data_entities.append(DataEntity(**data_entity_dict))
                # Extract date:
                date = datetime.datetime.strptime(deserialized.pop('date'),
                                                  "%Y-%m-%dT%H:%M:%S")
                return Dataset(**deserialized, tags=tags, date=date,
                               data_entities=data_entities)
            case _:
                raise ValueError("Unsupported type of object")

    @property
    def dictionary(self) -> dict:
        """Serialize sites to JSON serializable dictionary

        Returns:
            dict: JSON serializable dictionary representation of sites.
        """
        json_def = {}
        for _var in vars(self):
            if not _var.startswith("_"):
                json_def[_var] = getattr(self, _var)
        # Serialize entities:
        all_entities = []
        for page in self._list_of_pages:
            all_entities.append(page.dictionary)
        for article in self._list_of_articles:
            all_entities.append(article.dictionary)
        for data_entity in self._list_of_datasets:
            all_entities.append(data_entity.dictionary)
        json_def['list_of_entities'] = all_entities
        return json_def

    @property
    def json(self) -> str:
        """Serialize sites to JSON

        Returns:
            str: JSON representation of sites
        Note:
            - Cannot directly call .dictionary property as some entities
                require custom JSON encoders.
        """
        json_def = {}
        for _var in vars(self):
            if not _var.startswith("_"):
                json_def[_var] = getattr(self, _var)
        # Serialize entities:
        all_entities = []
        for page in self._list_of_pages:
            all_entities.append(json.loads(page.json))
        for article in self._list_of_articles:
            all_entities.append(json.loads(article.json))
        for data_entity in self._list_of_datasets:
            all_entities.append(json.loads(data_entity.json))
        json_def['list_of_entities'] = all_entities
        # Serialize result
        return json.dumps(json_def, cls=self.JSON_ENCODER)

    @classmethod
    def sites_from_json(cls, json_obj: str | dict) -> 'Sites':
        """Deserialize sites from JSON string.
        Args:
            json_obj (str): Input JSON string or dictionary.
        Returns:
            Sites: new sites from JSON string.
        """
        if isinstance(json_obj, str):
            deserialized: dict = json.loads(json_obj)
        else:
            deserialized: dict = copy.deepcopy(json_obj)

        list_of_entities = deserialized.pop('list_of_entities')
        entities = []
        for entity_def in list_of_entities:
            entities.append(cls.object_from_json(entity_def))
        deserialized['list_of_entities'] = entities
        return cls(**deserialized)

    def archive(self,
                archive_file_path: Path,
                content_file_name: str = "content.json",
                config_file_name: str = "config.json",
                layouts_dir_name: str = "LAYOUTS",
                resources_dir_name: str = "RESOURCES") -> None:
        """Archive the whole sites (including layouts and resources) to
            the archive ZIP file.

        Args:
            archive_file_path (Path): Path to the ZIP file. Rewrite its
                content if exists or create a new one.
            content_file_name (str): Name of file for JSON content of sites.
            config_file_name (str): Name of JSON with configuration.
            layouts_dir_name (str): Name of directory for layouts.
            resources_dir_name (str): Name of directory for resources.
        """
        # Create a temporary directory for outputs
        archive_dir = tempfile.mkdtemp()

        # Create a file for web-site text content in JSON
        content_path_to_json: Path = Path(archive_dir, content_file_name)
        with content_path_to_json.open('w') as cont_fp:
            cont_fp.write(self.json)

        # Archive Config class
        config_path_to_json: Path = Path(archive_dir, config_file_name)
        with config_path_to_json.open('w') as config_fp:
            config_fp.write(Config.to_json())

        # Copy layouts
        shutil.copytree(Config.templates_path,
                        Path(archive_dir, layouts_dir_name),
                        dirs_exist_ok=True)

        # Copy resources
        if Config.resources_path:
            shutil.copytree(Config.resources_path,
                            Path(archive_dir, resources_dir_name),
                            dirs_exist_ok=True)

        # Create archive
        shutil.make_archive(str(archive_file_path), 'zip', archive_dir)

        # Remove archive directory
        shutil.rmtree(archive_dir)
