import json
from pathlib import Path
from typing import Optional, Any

import classutilities


class Config(classutilities.ClassPropertiesMixin):
    """Configuration of the application.

    Attributes:
        templates_path (Path): Path to the folder with templates.
        resources_path (Optional[Path]): Path to directory with resources. If
            set, the content of the directory is copied to the output folder.
        css_style_path (Optional[Path]): Path to CSS styles (for copying).
        default_layout_template (str): A default template file for websites.
        default_page_template (str): A default template for the page.
        default_article_template (str): A default template for the article.
        default_dataset_template (str): A default template for the dataset.
        default_dataset_list_template (str): A Default template for dataset
            listing with pagination.
        maximal_article_tag_cloud_size (int): The maximal number of elements
            in articles tag cloud.
        default_article_tag_cloud_template (str): A default template to
            generate article tag cloud.
        title_article_tag_cloud (str): Title of article's tag cloud
        maximal_dataset_tag_cloud_size (int): The maximal number of elements
            in the dataset's tag cloud.
        default_dataset_tag_cloud_template (str): A default template to
            generate the dataset's tag cloud.
        title_dataset_tag_cloud (str): A title of the dataset's tag cloud.
        default_menu_template (str): A default template for the menu.
        default_recent_posts_template (str): A default template for
            recent posts.
        maximal_recent_posts (int): The maximal number of recent posts to show.
        recent_posts_title (str): A title for the recent posts tag.
        default_recent_datasets_template (str): A default template for
            the recent datasets.
        maximal_recent_datasets (int): The maximal number of the recent
            datasets to show.
        recent_datasets_title (str): A title for the recent datasets tag.
        site_title (str): Name of sites (tag title in tag head in HTML).
        site_logo_text (str): Text for website logo.
        site_title_separator (str): Separator for specific page for the title
            tag in tag head.
        site_title_homepage (str): Particular site name for the homepage.
            Applies if the name is not defined explicitly.
        site_home_file_name (str): Name of the file that is meant to be
            a homepage (typically 'index.html' or 'index.htm', but NEVER '/')
        site_home_url (str): The URL path to homepage (preferably '/' or
            'index.html').
        site_file_suffix (str): Suffix for the generated HTML files
            (typically '.html' or '.htm').
        pagination_prefix (str): Prefix for the pagination suffix (applies if
            the pagination is not on the homepage). Typically '-': the result
            in pagination URL follows the logic: WHATEVER-page-5.
        pagination_suffix (str): Suffix for pagination, typically 'page-' =>
            results in pagination URL follows the logic: WHATEVER-page-5.
        pagination_max_item_per_page (int): Number of entities per page.
            Important for defining pagination.
        footer (str): Footer for the website.
        append_to_head_tag (str): A string that is appended into the head tag
            in every HTML page.
        append_to_menu (tuple[dict[str, str | int]]): Tuple of items that are
            added to the menu. Contains dictionaries with keys: 'title' which
            is the displayed name of the item, 'url' which is the link to
            a page (or __HOME_PAGE__ if the homepage is meant to be the target,
            or __BLOG__ if the default blog is target, or __DATASET__ if
            default dataset listing is target), 'menu_position' which is the
            position inside menu.
        time_format (str): Time format to be used for the datetime.strftime
            function call.
        site_map_template (str): Path to the site-map template.
        site_map_url_prefix (str): URL prefix for site-map (it always should
            be a reference to existing URL, e. g. "http://example.com/").
        robots_txt (str): The content of the robots.txt file.
        tag_url_prefix (str): A prefix for tag's URLs.
        template_parameters (dict[str, Any]): Global additional template
            engine parameters, variable can be accessed in any template.
        blog_url (Optional[str]): A default URL for the dedicated blog page
            (if None, the dedicated blog page is not generated).
        blog_title (str): Title of the dedicated blog page.
        dataset_url (Optional[str]): A default URL for the dedicated data
            catalogue page (if None, the dedicated data catalogue page is
            not generated).
        dataset_title (str): Title of the dedicated data catalogue page.
    """
    # Path to the templates
    templates_path: Path = Path(Path(__file__).parent, 'templates')
    resources_path: Optional[Path] = None

    # Path to CSS styles
    css_style_path: Optional[Path] = Path(Path(__file__).parent,
                                          'templates', 'style.css')

    # Template for whole sites
    default_layout_template: str = "layout.jnj"

    # Template to article
    default_article_template: str = "article.jnj"

    # Template to page
    default_page_template: str = "article.jnj"

    # Template to page
    default_dataset_template: str = "dataset.jnj"

    # List template
    default_dataset_list_template: str = "dataset_list.jnj"

    # Template to article list
    default_article_list_template: str = "article_list.jnj"

    # Article tag cloud configuration
    maximal_article_tag_cloud_size: int = 5
    default_article_tag_cloud_template: str = "tag_cloud.jnj"
    title_article_tag_cloud: str = "Article tag cloud"

    # Dataset tag cloud configuration
    maximal_dataset_tag_cloud_size: int = 5
    default_dataset_tag_cloud_template: str = "tag_cloud.jnj"
    title_dataset_tag_cloud: str = "Dataset tag cloud"

    # Menu configuration
    default_menu_template: str = "menu.jnj"

    # Recent posts configuration
    default_recent_posts_template: str = "recent_entities.jnj"
    maximal_recent_posts: int = 5
    recent_posts_title: str = "Recent posts"

    # Recent datasets configuration
    default_recent_datasets_template: str = "recent_entities.jnj"
    maximal_recent_datasets: int = 5
    recent_datasets_title: str = "Recent datasets"

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
    text_sections_in_right_menu: tuple[dict[str, str]] = (
        {
            "header": "About",
            "content": 'Generated using <a href="http://crinita.salispace.com/">Crinita</a>.'  # noqa: E501
        },
    )

    # Default footer of page
    footer: str = '<p><a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />All the content is licensed under a <br><a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.</p>'  # noqa: E501
    append_to_head_tag: str = '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,400;0,700;1,400;1,700&display=swap" rel="stylesheet">'''  # noqa: E501

    # Default meta tags values
    default_meta_description = "Some blog"
    default_meta_keywords = "blog, posts"
    default_meta_meta_author = "Crinita"

    # Menu configuration
    append_to_menu: tuple[dict[str, str | int]] = (
        {
            "title": "HOME",
            # Either __HOME_PAGE__, __BLOG__, or __DATASET__ or External Link
            "url": "__HOME_PAGE__",
            "menu_position": 0
        },
        {
            "title": "External link",
            "url": "http://github.com",
            "menu_position": 21
        },
    )

    # Time format for datetime.datetime.strftime transformation
    time_format: str = "%B %d, %Y"

    # Site map template
    site_map_template: str = 'site_map.jnj'

    # URL prefix for sitemap
    site_map_url_prefix: str = ''

    # Robots.txt content
    robots_txt: str = """User-agent: *
Allow: /
Sitemap: sitemap.xml"""

    # Prefix for tag
    tag_url_prefix: str = "tag-"

    # URL for blog page (if referenced directly in menu)
    blog_url: Optional[str] = "blog"  # Of None, nothing is generated
    blog_title: str = "Blog"

    # URL for dataset page (if referenced directly in menu)
    dataset_url: Optional[str] = "catalogue"  # Of None, nothing is generated
    dataset_title: str = "Data catalogue"

    template_parameters: dict[str, Any] = None

    @classmethod
    @property
    def global_template_parameters(cls) -> dict[str, Any]:
        if cls.template_parameters:
            return cls.template_parameters
        return {}

    # Functionality for serialization to JSON:
    @classmethod
    def to_json(cls) -> str:
        """Serialize to JSON.
        Returns:
            str: JSON representation of Config class
        """
        return json.dumps(cls.json)

    @classutilities.classproperty
    def json(cls) -> dict:
        """Dictionary representation of the Config class"""
        json_def = {}
        for _var in vars(cls):
            if _var == "json":
                continue
            if _var.startswith("_"):
                continue
            if callable(getattr(cls, _var)):
                continue
            json_def[_var] = getattr(cls, _var)
            if isinstance(json_def[_var], Path):
                json_def[_var] = str(json_def[_var])
        # Serialize the object type name
        json_def['object_type'] = cls.__name__
        return json_def

    @json.setter
    def json(cls, value: dict):
        """Set configuration from dictionary"""
        object_type = value.pop('object_type')
        if object_type != cls.__name__:
            raise ValueError(f"Value of object_type has to be {cls.__name__}")

        path_vars = set()
        for _var in vars(cls):
            if isinstance(getattr(cls, _var), Path):
                path_vars.add(_var)

        for _key, _val in value.items():
            setattr(cls, _key, _val)
            if _key in path_vars:
                if _val is not None:
                    setattr(cls, _key, Path(_val))
                else:
                    setattr(cls, _key, None)

    @classmethod
    def from_json(cls, json_str: str) -> None:
        """Set-up class from JSON.

        Args:
            json_str (str): JSON definition of Config class.
        """
        cls.json = json.loads(json_str)  # Deserialize JSON
