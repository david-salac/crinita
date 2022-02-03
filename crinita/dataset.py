from typing import Optional, Any
import datetime
from pathlib import Path
from dataclasses import dataclass

from .entity_detail import EntityDetail
from .config import Config
from .tag import Tag, JSONEncoderWithTags


@dataclass
class DataEntity(object):
    """Represents a single data entity in a dataset.

    Attributes:
        title (str): Name of the file (title)
        data_link (str): Link where data are available (or downloadable).
        description (Optional[str]): Description of data entity.
        license (Optional[str]): License string.
        icon (Optional[str]): Image (icon) visualising data type.
        extension (Optional[str]): Extension of the file (used in preview).
    """
    title: str
    data_link: str
    description: Optional[str] = None
    license: Optional[str] = None
    icon: Optional[str] = None
    extension: Optional[str] = None

    def keys(self) -> list[str]:
        """Get keys that allows conversion of this class to dictionary.

        Returns:
            list[str]: List of the keys.
        """
        return ['title', 'data_link', 'description', 'license', 'icon',
                'extension']

    def __getitem__(self, key):
        """Allows conversion of this class to dictionary.
        """
        return getattr(self, key)


class JSONEncoderWithTagsAndDataEntities(JSONEncoderWithTags):
    """Allow to serialize data entities to JSON"""
    def default(self, o: Any) -> Any:
        if isinstance(o, DataEntity):
            return dict(o)
        elif isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        return super().default(o)


class Dataset(EntityDetail):
    """Represents a single dataset entity (an entity of data catalogue).

    Attributes:
        large_image_path (str): Path to the large image (background one).
        small_image_path (str): Path to the small image (icon).
        tags (list[Tag]): Tags related to the dataset.

        date (datetime.datetime): Date when dataset was published.
        lead (str): Lead of the dataset.
        content (str): Content of the dataset.

        data_entities (list[DataEntity]): Concrete data entities contained in
            a dataset (data catalogue item).
        data_source (Optional[str]): Source and info about data origin.
        maintainer (Optional[str]): Info and contact about data maintainer.
        license (Optional[str]): License info.
    """
    JSON_ENCODER = JSONEncoderWithTagsAndDataEntities

    def __init__(
        self,
        title: str,
        url_alias: str,
        date: datetime.datetime,
        lead: str,
        content: str,
        tags: list[Tag] = tuple(),

        data_entities: list[DataEntity] = tuple(),
        data_source: Optional[str] = None,
        maintainer: Optional[str] = None,
        license: Optional[str] = None,

        large_image_path: Optional[str | Path] = None,
        small_image_path: Optional[str | Path] = None,
        template: str = '__DEFAULT__',
        description: Optional[str] = None,
        keywords: Optional[str] = None,
        template_parameters: dict[str, Any] = None
    ):
        """Create the new dataset.

        Args:
            template (str): A name of the file with Jinja2 template.
                If __DEFAULT__, the default template from Config class is used.
            title (str): Name of the dataset.
            description (Optional[str]): Description of the page (applies
                in meta tag); If None, lead is used instead.
            keywords (Optional[str]): Keywords related to the page (meta tag);
                if None, tag names are used.
            url_alias (str): Alias for the page (like my-page).
            tags (list[Tag]): List of tags of the dataset.

            large_image_path (Optional[str | Path]): Path to the large image
                (usually the background one).
            small_image_path (Optional[str | Path]): Path to the small image
                (usually the icon).
            date (datetime.datetime): Date when dataset was published.

            lead (str): Lead of the entity (short description).
            content (str): Content of the dataset (longer description).
            template_parameters (dict[str, Any]): All other additional
                parameters that are passed to the template engine.

            data_entities (list[DataEntity]): Concrete data entities.
            data_source (Optional[str]): Source and info about data origin.
            maintainer (Optional[str]): Info and contact about data maintainer.
            license (Optional[str]): License info.
        """
        if template == "__DEFAULT__":
            template = Config.default_dataset_template

        # Call the entity constructor to pass meta tags
        if keywords is None and len(tags) > 0:
            keywords = ", ".join([single_tag.name for single_tag in tags])

        super().__init__(template, title, description, keywords, url_alias,
                         template_parameters=template_parameters)

        self.tags: list[Tag] = tags

        self.large_image_path: Optional[str] = (str(large_image_path)
                                                if large_image_path else None)
        self.small_image_path: Optional[str] = (str(small_image_path)
                                                if small_image_path else None)
        self.date: datetime.datetime = date
        self.lead: str = lead
        self.content: str = content

        self.data_entities: list[DataEntity] = data_entities
        self.data_source: Optional[str] = data_source
        self.maintainer: Optional[str] = maintainer
        self.license: Optional[str] = license

    def keys(self) -> list[str]:
        """Get keys that allows conversion of this class to dictionary.

        Returns:
            list[str]: List of the keys to be passed to template.
        """
        return ['tags', 'title', 'small_image_path', 'large_image_path',
                'date', 'lead', 'content',
                'data_entities', 'data_source', 'maintainer', 'license']

    def __getitem__(self, key):
        """Allows conversion of this class to dictionary.
        """
        if key == 'date':
            return self.date.strftime(Config.time_format)
        return getattr(self, key)

    @property
    def extensions(self) -> Optional[set[str]]:
        """Returns used file extensions"""
        used_extensions: set[str] = set([_ext['extension']
                                        for _ext in self.data_entities])
        if None in used_extensions:
            used_extensions.discard(None)
        if len(used_extensions) == 0:
            return None
        return used_extensions
