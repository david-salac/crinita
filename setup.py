import setuptools
import re

# Read README.md
with open("README.md", "r") as fh:
    long_description = fh.read()

# Get the Crinita's version
version_file = open("crinita/__init__.py", 'rt').read()
version_regexp = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(version_regexp, version_file, re.M)
if mo:
    crinita_version = mo.group(1)
else:
    raise RuntimeError("Unable to find version string.")

# Read requirements
with open('requirements.txt') as f:
    crinita_requirements: list[str] = f.read().splitlines()

setuptools.setup(
    name="crinita",
    version=crinita_version,
    author="David Salac",
    author_email="info@davidsalac.eu",
    description="Crinita is a Python application for generating static "
                "websites like blogs, data catalogues or simple static pages. "
                "It directly creates HTML files based on inputs (without "
                "requiring to run any script languages on the server-side).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://crinita.salispace.com",
    packages=setuptools.find_packages(),
    package_data={'': ['templates/*']},
    install_requires=crinita_requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
