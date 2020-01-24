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
            id = "null"
        if uid is None:
            uid = "null"
        if title is None:
            title = "No title assigned to this dashboard"
        if timezone is None:
            timezone = "browser"
        if schemaVersion is None:
            schemaVersion = "21"
        if version is None:
            version = "0"
            
        self.id = id
        self.uid = uid
        self.title = title
        self.timezone = timezone
        self.schemaVersion = schemaVersion
        self.version = version
        self.json_representation = ""
        
    def get_json_string(self):
        return "\"id\": {},\"uid\": {},\"title\": \"{}\",\"timezone\": \"{}\",\"schemaVersion\": {},\"version\": {}".format(self.id, self.uid, self.title, self.timezone, self.schemaVersion, self.version)

class Panel:
    pass