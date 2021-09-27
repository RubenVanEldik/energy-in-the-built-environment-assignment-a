import json


def save_json_file(obj, *, filepath):
    """
    Save a object or list as a JSON file

    Parameters:
        obj (dict or list): Dictionary or list that should be stored
        filepath (string): Path of where the JSON file should be stored
    """
    with open(filepath, 'w') as fp:
        json.dump(obj, fp, indent=2, ensure_ascii=False)


def save_text_file(text, *, filepath):
    """
    Save a string as a text file

    Parameters:
        text (str): String that should be stored
        filepath (string): Path of where the JSON file should be stored
    """
    with open(filepath, 'w') as output:
        output.write(text)
