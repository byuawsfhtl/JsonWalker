import setuptools
import os
from JsonWalker._version import __version__ as version

APP_NAME = "JsonWalker"

with open("README.md", "r", encoding="utf-8") as fh:
    longDescription = fh.read()

def listFolders(directory: str) -> list:
    """Lists all the folders in a directory.

    Args:
        directory (str): the directory to search

    Returns:
        list: a list of all the folders in the directory
    """
    folders = []
    for item in os.listdir(directory):
        itemPath = os.path.join(directory, item)
        if os.path.isdir(itemPath) and item != "__pycache__":
            folders.append(itemPath)
    otherFolders = [listFolders(itemPath) for itemPath in folders]
    for folder in otherFolders:
        folders.extend(folder)
    return folders

folderPath = APP_NAME
folders = listFolders(folderPath)
folders.append(APP_NAME)
print(folders)

setuptools.setup(
    name=APP_NAME,
    version=version,
    author='Record Linking Lab',
    author_email='recordlinkinglab@gmail.com',
    description='This is a easy to use library for walking through json data.',
    long_description=longDescription,
    long_description_content_type="text/markdown",
    url='https://github.com/byuawsfhtl/JsonWalker.git',
    project_urls = {
        "Bug Tracker": "https://github.com/byuawsfhtl/JsonWalker/issues"
    },
    packages=folders,
    install_requires=[]
)