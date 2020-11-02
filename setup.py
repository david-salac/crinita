import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="crinita",
    version="0.0.8",
    author="David Salac",
    author_email="info@davidsalac.eu",
    description="Python application for generating static websites like"
                " a blog or simple static pages. Creates HTML files based"
                " on inputs (without requiring to run any script languages"
                " on the server-side).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/david-salac/crinita",
    packages=setuptools.find_packages(),
    install_requires=['Jinja2', ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
