from pathlib import Path

from _version import __version__

def getActiveBranchName() -> str:
    """Get the name of the active branch.

    Returns:
        str: the name of the active branch
    """
    headDir = Path(".") / ".git" / "HEAD"
    with headDir.open("r") as f: content = f.read().splitlines()

    for line in content:
        if line[0:4] == "ref:":
            return line.partition("refs/heads/")[2]
        
def updatePrdVersion(oldVersion: str) -> str:
    """Update the version number for the production branch.

    Args:
        oldVersion (str): the current version number

    Returns:
        str: the new version number
    """
    # Should never come from dev
    # Came from stg
    if 'b' in oldVersion:
        oldVersion = oldVersion.split('b')[0]
        newVersion = oldVersion.split('.')
        newVersion[-1] = str(int(newVersion[-1]) + 1)
        newVersion = '.'.join(newVersion)
    # Came from prd
    else:
        newVersion = oldVersion.split('.')
        newVersion[-1] = str(int(newVersion[-1]) + 1)
        newVersion = '.'.join(newVersion)
    return newVersion

def updateStgVersion(oldVersion: str) -> str:
    """Update the version number for the staging branch.

    Args:
        oldVersion (str): the current version number

    Returns:
        str: the new version number
    """
    # Came from dev
    if '.dev' in oldVersion:
        oldVersion = oldVersion.split('.dev')[0]
        newVersion = oldVersion.split('b')
        newVersion[-1] = str(int(newVersion[-1]) + 1)
        newVersion = 'b'.join(newVersion)
    # Came from stg
    elif 'b' in oldVersion:
        newVersion = oldVersion.split('b')
        newVersion[-1] = str(int(newVersion[-1]) + 1)
        newVersion = 'b'.join(newVersion)
    # Came from prd
    else:
        newVersion = oldVersion + 'b0'
    return newVersion

def updateDevVersion(oldVersion: str) -> str:
    """Update the version number for the development branch.

    Args:
        oldVersion (str): the current version number

    Returns:
        str: the new version number
    """
    # Came from dev
    if '.dev' in oldVersion:
        newVersion = oldVersion.split('.dev')
        newVersion[-1] = str(int(newVersion[-1]) + 1)
        newVersion = '.dev'.join(newVersion)
    # Came from stg
    elif 'b' in oldVersion:
        newVersion = oldVersion + '.dev0'
    # Should never come from prd
    return newVersion
        

if __name__ == '__main__':
    """Auto-update the version number based on the current branch."""
    oldVersion = __version__
    branch = getActiveBranchName()

    if branch == 'prd':
        newVersion = updatePrdVersion(oldVersion)
    elif branch == 'stg':
        newVersion = updateStgVersion(oldVersion)
    elif branch == 'dev':
        newVersion = updateDevVersion(oldVersion)
    else:
        newVersion = oldVersion

    with open("_version.py", "w") as f:
        f.write(f'__version__ = \'{newVersion}\'')

    print(f'Auto-updated version from {oldVersion} to {newVersion}')