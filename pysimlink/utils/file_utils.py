import os

def get_other_in_dir(directory, known):
    """
    :param directory: path to the directory
    :param known: The file/folder known to exist in the directory

    Return the other directory/file in the directory
    """

    model_folders = set(os.listdir(directory))
    model_folders.discard('.DS_Store')
    assert len(model_folders) == 2, \
        f"Directory '{directory}' contains more than 2 folders (not counting .DS_Store on Mac)"
    assert known in model_folders, \
        f"File does not exist in {directory}. Should be one of {model_folders}"
    model_folders.remove(known)

    return model_folders.pop()

