class Dashboard:
    def __init__(self, panels = None, properties = None):
        self.properties          = properties
        self.panels              = panels
        self.json_representation = ""

    def get_json_string(self):
        return "{}".format(self.properties.get_json_string())

class Dashboard_Properties:
    def __init__(self, id = None, uid = None, title = None, timezone = None, schemaVersion = None, version = None):
        if id is None:
            self.id = "null"
        if uid is None:
            self.uid = "null"
        if title is None:
            self.title = "No title assigned 2"
        if timezone is None:
            self.timezone = "browser"
        if schemaVersion is None:
            self.schemaVersion = "21"
        if version is None:
            self.version = "0"
        self.json_representation = ""
        
    def get_json_string(self):
        return "\"id\": {},\"uid\": {},\"title\": \"{}\",\"timezone\": \"{}\",\"schemaVersion\": {},\"version\": {}".format(self.id, self.uid, self.title, self.timezone, self.schemaVersion, self.version)

class Panel:
    pass