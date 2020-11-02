from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Dict


@dataclass
class Config(object):
    """Configuration of the application.

    Attributes:
        templates_path (Path): Path to the folder with templates.
        default_css_style_path (Path): Path to css styles
        default_layout_template (str): Default template file for websites.
        default_page_template (str): Default template for the page.
        default_article_template (str): Default template for the article.
        maximal_tag_cloud_size (int): Maximal number of elements in tag cloud.
        default_tag_cloud_template (str): Template to generate tag cloud.
        default_menu_template (str): Template for the menu.
        default_recent_posts (str): Template for the recent posts.
        maximal_recent_posts (int): Maximal number of recent posts to show.
        site_title (str): Name of sites (tag title in the tag head).
        site_logo_text (str): Text for the site logo.
        site_title_separator (str): Separator for specific page for the title
            tag in tag head.
        site_title_homepage (str): Particular site name for the homepage.
            Applies only if name is not defined explicitly.
        site_home_file_name (str): Name of the file that is meant to be
            a homepage (typically 'index.html' or 'index.htm', but NEVER '/')
        site_home_url (str): URL path to the homepage (preferably '/' or
            'index.html').
        site_file_suffix (str): Suffix for the files generation (typically
            '.html' or '.htm').
        pagination_prefix (str): Prefix for pagination suffix (applies only if
            the pagination is not on homepage), typically '-' => results in
            pagination url following logic: something-page-5.
        pagination_suffix (str): Suffix for pagination, typically 'page-' =>
            results in pagination url following logic: something-page-5.
        pagination_max_item_per_page (int): Number of articles per page.
        footer (str): Footer of the page.
        append_to_head_tag (str): Text that is appended to the header tag
            in the HTML page (before the style is imported).
        append_to_menu (Tuple[Dict[str, str]]): Tuple of items that are added
            to the menu. Contains dictionaries with keys: 'title' which is the
            name of the item, 'url' which is the link (__HOME_PAGE__ if the
            homepage is meant to be the target), 'menu_position' which is the
            position inside menu.
        time_format (str): Time format to be used for the datetime.strftime
            function call.
        site_map_template (str): Path to the site-map template.
        robots_txt (str): Content of the robots.txt file.
        tag_url_prefix (str): Prefix for tag URLs.
    """
    # Path to the templates
    templates_path: Path = Path(Path(__file__).parent, 'templates')

    # Path to CSS styles
    default_css_style_path: Path = Path('style.css')

    # Template for whole sites
    default_layout_template: str = "layout.jnj"

    # Template to article
    default_article_template: str = "article.jnj"

    # Template to page
    default_page_template: str = "article.jnj"

    # Template to article list
    default_article_list_template: str = "article_list.jnj"

    # Tag cloud configuration
    maximal_tag_cloud_size: int = 5
    default_tag_cloud_template: str = "tag_cloud.jnj"

    # Menu configuration
    default_menu_template: str = "menu.jnj"

    # Recent posts configuration
    default_recent_posts: str = "recent_posts.jnj"
    maximal_recent_posts: int = 5

    # Configuration of page title (tag title in head)
    site_title: str = "Some blog"
    site_logo_text: str = "SOME BLOG"
    site_title_separator: str = " | "
    site_title_homepage: str = "personal blog"

    # URL to the homepage
    site_home_url: str = 'index.html'  # typically '/'

    # File that contains homepage
    site_home_file_name: str = "index.html"

    # Suffix for the pages (files suffix)
    site_file_suffix: str = ".html"

    # Pagination configuration
    pagination_prefix: str = "-"  # applies only if url_alias is not None
    pagination_suffix: str = "page-"
    pagination_max_item_per_page: int = 7

    # Text in right menu
    default_text_sections_in_right_menu_template: str = 'text_in_menu.jnj'
    text_sections_in_right_menu: Tuple[Dict[str, str]] = (
        {
            "header": "About",
            "content": 'Generated using <a href="http://www.crinita.com/">Crinita</a>.'  # noqa: E501
        },
    )

    # Default footer of page
    footer: str = '<p><a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />All the content is licensed under a <br><a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.</p>'  # noqa: E501
    append_to_head_tag: str = '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400;1,700&display=swap" rel="stylesheet">'  # noqa: E501

    # Default meta tags values
    default_meta_description = "Some blog"
    default_meta_keywords = "blog, posts"
    default_meta_meta_author = "Crinita"

    # Menu configuration
    append_to_menu: Tuple[Dict[str, str]] = (
        {
            "title": "HOME",
            "url": "__HOME_PAGE__",  # Either __HOME_PAGE__ or external link
            "menu_position": 0
        },
        {
            "title": "Smth external",
            "url": "http://github.com",
            "menu_position": 21
        },
    )

    # Time format for datetime.datetime.strftime transformation
    time_format: str = "%B %d, %Y"

    # Site map template
    site_map_template: str = 'site_map.jnj'

    # Robots.txt content
    robots_txt: str = """User-agent: *
Allow: /
Sitemap: sitemap.xml"""

    # Prefix for tag
    tag_url_prefix: str = "tag-"
