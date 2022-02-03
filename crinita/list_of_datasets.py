from typing import Optional, Any

from .config import Config
from .dataset import Dataset
from .entity_list import EntityList


class ListOfDatasets(EntityList):
    """Generate the list of datasets (data catalogue) with pagination.
    """

    def __init__(
        self,
        title: str,
        list_of_entities: list[Dataset],
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
            list_of_entities (list[Dataset]): List of all datasets to be
                considered for pagination.
            template_parameters (dict[str, Any]): All other additional
                parameters that are passed to the template engine.
        """
        if template == "__DEFAULT__":
            template = Config.default_dataset_list_template
        # Call the entity constructor to pass meta tags
        super().__init__(title, list_of_entities, url_alias, template,
                         description, keywords,
                         template_parameters=template_parameters)
