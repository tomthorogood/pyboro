from setuptools import setup, find_packages

readme = None
with open("README.md") as readme_md:
    readme = readme_md.read()

setup(
        name = "pyboro",
        version = "0.4.0",
        description = "pyboro is a utility for lexing and consuming input by setting up regular expression tables and building syntax maps.",
        long_description = readme,
        author = "Tom A. Thorogood",
        author_email = "tom@tomthorogood.com",
        license = "GPLv3",
        url="http://www.github.com/tomthorogood/pyboro",
        packages = find_packages(exclude=['setup.py','tests']),
        zip_safe = True
)


