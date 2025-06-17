import setuptools
import os
from JsonWalker._version import __version__ as version

APP_NAME = "JsonWalker"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def list_folders(directory: str) -> list:
    """Lists all the folders in a directory.

    Args:
        directory: the directory to search

    Returns:
        a list of all the folders in the directory
    """
    folders = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path) and item != "__pycache__":
            folders.append(item_path)
    other_folders = [list_folders(item_path) for item_path in folders]
    for folder in other_folders:
        folders.extend(folder)
    return folders

folder_path = APP_NAME
folders = list_folders(folder_path)
folders.append(APP_NAME)
print(folders)

setuptools.setup(
    name=APP_NAME,
    version=version,
    author='Record Linking Lab',
    author_email='recordlinkinglab@gmail.com',
    description='This is a easy to use library for walking through json data.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/byuawsfhtl/JsonWalker.git',
    project_urls = {
        "Bug Tracker": "https://github.com/byuawsfhtl/JsonWalker/issues"
    },
    packages=folders,
    install_requires=[]
)