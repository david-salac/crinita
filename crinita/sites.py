from typing import List, Dict, Set, Optional, Union
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache

from jinja2 import Environment, FileSystemLoader

from .config import Config
from .utils import Utils
from .article import Article, Tag
from .entity import Entity
from .page import Page
from .list_of_articles import ListOfArticles


@dataclass()
class _SinglePageHTML(object):
    """Dataclass for generation of the HTML page from layout.
    """
    title: str
    menu: str
    page_content: str
    recent_posts: str
    tag_cloud: str
    text_section_in_right_menu: str
    meta_description: str = None
    meta_keywords: str = None
    meta_author: str = None
    css_style_file: str = None
    append_to_head_tag: str = None
    homepage_link: str = None
    site_logo_text: str = None
    footer: str = None

    def keys(self) -> List[str]:
        """Get keys that allows conversion of this class to dictionary.

        Returns:
            List[str]: List of the keys to be passed to template.
        """
        return [atr for atr in vars(self) if '__' not in atr]

    def __getitem__(self, key):
        """Allows conversion of this class to dictionary.
        """
        return getattr(self, key)

    def write_to_file(
        self,
        file_path: Path,
        layout_template_path: Path
    ) -> None:
        """Write page content to the HTML file.

        Args:
            file_path (Path): Path to the file
            layout_template_path (Path): Path to the layout template
        """
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
        if self.css_style_file is None:
            self.css_style_file = str(Config.default_css_style_path)
        if self.site_logo_text is None:
            self.site_logo_text = Config.site_logo_text
        if self.homepage_link is None:
            self.homepage_link = Config.site_home_url

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
        _tag_to_incidence: List of tag in the system (ordered by incidence from
            maximal to minimal).
        _tag_to_articles: Mapping from tag to list of articles.

        tag_cloud_template (str): Template file for the tag cloud.
        menu_template (str): Template file for the menu.
        recent_posts_template (str): Template file for the recent posts.
        site_map_urls (List[str]): List of all URLs in the app
    """

    def __init__(
        self,
        list_of_entities: List[Union[Article, Page]], *,
        check_url_unique: bool = True,
        layout_template: str = "__DEFAULT__",
        tag_cloud_template: str = "__DEFAULT__",
        menu_template: str = "__DEFAULT__",
        recent_posts_template: str = "__DEFAULT__",
        text_sections_in_right_menu_template: str = "__DEFAULT__",
    ):
        """Create a new sites

        Args:
             list_of_entities (List[Union[Article, Page]]): List of all pages
                and articles to be included.
             check_url_unique (bool): If True, uniqueness of URLs is checked.
             layout_template (str): Template file for the whole sites.
             tag_cloud_template (str): Template file for the tag cloud.
             menu_template (str): Template file for the menu.
             recent_posts_template (str): Template file for the recent posts.
             text_sections_in_right_menu_template (str): Template for the text
                section in right menu.
        """
        # Separate Page and Article instances from all entities
        list_of_articles: List[Article] = [
            art for art in list_of_entities if isinstance(art, Article)
        ]
        list_of_pages: List[Page] = [
            art for art in list_of_entities if isinstance(art, Page)
        ]

        self.tag_cloud_template: str = tag_cloud_template
        self.menu_template: str = menu_template
        self.recent_posts_template: str = recent_posts_template
        self.text_sections_in_right_menu_template: str = \
            text_sections_in_right_menu_template
        self.sites_template: str = layout_template
        if layout_template == "__DEFAULT__":
            self.layout_template = Config.default_layout_template

        if check_url_unique:
            # For sanity check (uniqueness of URLs)
            all_urls: Set[str] = set([])
            number_of_elements: int = 0
        # Process articles
        self._list_of_articles: List[Article] = sorted(list_of_articles,
                                                       key=lambda x: x.date,
                                                       reverse=True)
        self._tag_to_articles: Dict[Tag, List[Article]] = defaultdict(list)
        self._tag_to_incidence: Dict[Tag, int] = defaultdict(int)
        for article in list_of_articles:
            if check_url_unique:
                # Add url to set (for sanity check)
                all_urls.add(article.url_alias)
                number_of_elements += 1
            # Handle tags
            for tag in article.tags:
                self._tag_to_articles[tag].append(article)
                self._tag_to_incidence[tag] += 1
        # Sort articles in tag by date of publishing
        for tag in self.list_of_tags:
            self._tag_to_articles[tag] = sorted(self._tag_to_articles[tag],
                                                key=lambda x: x.date,
                                                reverse=True)
        # Sort dictionary by values from the biggest to lowest
        self._tag_to_incidence = {
            k: v for k, v in sorted(self._tag_to_incidence.items(),
                                    key=lambda item: item[1],
                                    reverse=True)
        }
        # Process pages
        self._list_of_pages: List[Page] = sorted(
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

        self.site_map_urls: List[str] = []

    @lru_cache()
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

    def _generate_article_or_page(
        self,
        article_or_page: Union[Article, Page],
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
                article_or_page.url_alias, True
            )
        )
        if not rewrite_if_exists and target_file.exists():
            # Skip if existing files must not be rewritten.
            raise FileExistsError("this file already exists")
        # Write content to file
        _SinglePageHTML(
            page_content=article_or_page.generate_page(
                article_or_page.url_alias
            ),
            title=article_or_page.page_title,

            # Generate blocks
            meta_description=article_or_page.description,
            meta_keywords=article_or_page.keywords,
            menu=self.generate_menu(),
            recent_posts=self.generate_recent_posts(),
            tag_cloud=self.generate_tag_cloud(),
            text_section_in_right_menu=self.generate_text_sections_in_right_menu()  # noqa: E501
        ).write_to_file(target_file, self.layout_template)

        # Append to site map
        self.site_map_urls.append(article_or_page.url)

    def _generate_list_of_articles_with_pagination(
        self,
        tag: Tag,
        output_directory_path: Path,
        rewrite_if_exists: bool, *,
        list_page: Optional[ListOfArticles] = None
    ) -> None:
        """Generate all files related to the concrete tag in the system.

        Args:
            tag (Tag): Tag for that content is generated.
            output_directory_path (Path): Path where the output files are
                generated.
            rewrite_if_exists (bool): If True, files are rewritten; if False,
                exception is raised.
            list_page (Optional[ListOfArticles]): Entity that is used for
                pagination (if None, new entity is created from the tag).
        """
        if list_page is None:
            list_page: ListOfArticles = ListOfArticles(
                list_of_articles=self.tag_to_articles[tag],
                url_alias=tag.url_alias_with_prefix,
                tag=tag
            )
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
                page_content=list_page.generate_page(single_url),
                title=list_page.page_title,

                # Generate blocks
                meta_description=list_page.description,
                meta_keywords=list_page.keywords,
                menu=self.generate_menu(),
                recent_posts=self.generate_recent_posts(),
                tag_cloud=self.generate_tag_cloud(),
                text_section_in_right_menu=self.generate_text_sections_in_right_menu()  # noqa: E501
            ).write_to_file(target_file, self.layout_template)

            # Append to site map
            self.site_map_urls.append(Utils.generate_file_path(single_url))

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
        # Generate all articles
        for article in self.list_of_articles:
            self._generate_article_or_page(
                article_or_page=article,
                output_directory_path=output_directory_path,
                rewrite_if_exists=rewrite_if_exists
            )

        # Generate all pagination of articles
        if isinstance(self.homepage, ListOfArticles):
            self._generate_list_of_articles_with_pagination(
                tag=None,
                output_directory_path=output_directory_path,
                rewrite_if_exists=rewrite_if_exists,
                list_page=self.homepage
            )
        for tag in self.list_of_tags:
            self._generate_list_of_articles_with_pagination(
                tag=tag,
                output_directory_path=output_directory_path,
                rewrite_if_exists=rewrite_if_exists,
            )

        # Generate all pages
        for page in self.list_of_pages:
            self._generate_article_or_page(
                article_or_page=page,
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
                site_map_urls_with_prefix: List[str] = []
                for single_url in self.site_map_urls:
                    if single_url == '/':
                        # Causes troubles when merging routes
                        site_map_urls_with_prefix.append(
                            Config.site_map_url_prefix
                        )
                    else:
                        site_map_urls_with_prefix.append(
                            Path(Config.site_map_url_prefix).joinpath(
                                single_url
                            )
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
    def list_of_tags(self):  # Ordered by incidence
        return list(self._tag_to_incidence.keys())

    @property
    def tags_with_incidences(self):  # Ordered by incidence
        return self._tag_to_incidence

    @property
    def tag_to_articles(self):  # Ordered by date
        return self._tag_to_articles

    @property
    @lru_cache()
    def homepage(self) -> Entity:
        """Get the homepage of the sites. Technically the Entity that has
            url_alias set to None. If there is not any Entity, the new one
            is created as a list of all articles in the system.
        """
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

        # If there is no explicit homepage, generate as a list of all articles
        if homepage_ent is None:
            homepage_ent = ListOfArticles(self.list_of_articles)

        return homepage_ent
