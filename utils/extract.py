def get_nested_data(data, *path):
    """
    Extracts data from a nested dictionary using a series of string keys.

    Parameters:
    data (dict): The dictionary from which to extract data.
    *path (str): Variable number of string arguments that represent the path to the desired data.

    Returns:
    The extracted data or None if the path is invalid.
    """
    current = data
    for key in path:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current

# 使用例子
data = {
    'data': {
        'cards': 
            {'id': 2, 'name': 'Card2'}
    }
}


if __name__ == '__main__':
  cards = get_nested_data(data, 'data', 'cards','name')
  print(cards)
