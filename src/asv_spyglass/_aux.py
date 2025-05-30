from pathlib import Path


# Rename to something more descriptive, like `path_to_abs()`?
# Kanged from rgpycrumbs
def getstrform(pathobj: Path):
    return str(pathobj.absolute())
