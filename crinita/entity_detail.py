from typing import Optional, Any

from jinja2 import Environment, FileSystemLoader

from .entity import Entity
from .config import Config


class EntityDetail(Entity):
    """Abstract class that represents a detail view (not listing) of entity.
    """
    def __init__(
        self,
        template: str,
        title: str,
        description: Optional[str],
        keywords: Optional[str],
        url_alias: str,
        template_parameters: dict[str, Any] = None
    ):
        """Create the new blog post.
        """
        super().__init__(template, title, description, keywords, url_alias,
                         template_parameters=template_parameters)
        self.url_list = [url_alias]

    def generate_page(self,
                      url: str,
                      additional_tags: Optional[dict[str, Any]] = None) -> str:
        with open(Config.templates_path.joinpath(self.template)) as tem_han:
            # Create template specific parameters
            template_parameters = Config.global_template_parameters | \
                                  self.template_parameters

            template = Environment(
                loader=FileSystemLoader(Config.templates_path)
            ).from_string(tem_han.read())
            html_str = template.render(
                **dict(self), **template_parameters,
                additional_tags=(additional_tags if additional_tags else {})
            )
            return html_str
