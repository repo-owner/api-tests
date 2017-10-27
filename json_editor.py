import json


class JsonEditor:
    def __init__(self, dictionary):
        self.json = json.dumps(dictionary)

    def get_value_for_key(self, key):
        dictionary = json.loads(self.json)
        return dictionary[key]
