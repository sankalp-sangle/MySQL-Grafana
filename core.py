class Dashboard:
    def __init__(self, panels = None, properties = None):
        self.properties          = properties
        self.panels              = panels
        self.json_representation = ""

    def get_json_string(self):
        panelJSON = ""
        
        for panel in self.panels:
            panelJSON += "{" + panel.get_json_string() + "},"
        
        panelJSON = panelJSON[:-1]

        return "{}, \"panels\":[{}]".format(self.properties.get_json_string(), panelJSON)

class Dashboard_Properties:
    def __init__(self, id = None, uid = None, title = None, timezone = None, schemaVersion = None, version = None, time = None):
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
        if time is None:
            time = Time()
            
        self.id = id
        self.uid = uid
        self.title = title
        self.timezone = timezone
        self.schemaVersion = schemaVersion
        self.version = version
        self.json_representation = ""
        self.time = time

    def get_json_string(self):
        return "\"id\": {},\"uid\": {},\"title\": \"{}\",\"timezone\": \"{}\",\"schemaVersion\": {},\"version\": {},\"time\":{}".format(self.id, self.uid, self.title, self.timezone, self.schemaVersion, self.version, "{" + self.time.get_json_string() + "}")

class Panel:
    def __init__(self, datasource = None, id = None, title = None, panelType = None):
        if datasource is None:
            datasource = "MySQL"
        if id is None:
            id = "1"
        if title is None:
            title = "This is my sample panel title!"
        if panelType is None:
            panelType = "graph"

        self.datasource = datasource
        self.id = id
        self.title = title
        self.panelType = panelType

    def get_json_string(self):
        return "\"datasource\": \"{}\",\"id\": {},\"title\": \"{}\",\"type\":\"{}\"".format(self.datasource, self.id, self.title, self.panelType)

class Time:

    @staticmethod
    def convert_to_standard_format(timeFormat, requiresConversion):
            if requiresConversion:
                return "\"" + timeFormat[0:10] + "T00:00:00.000Z" + "\""
            return "\"" + timeFormat + "\""

    # Standard format : YYYY-MM-DD
    # Expected Grafana format : YYYY-MM-DDTHH:MM:SS.MSSZ

    def __init__(self, timeFrom = None, timeTo = None, fromRequiresConversion = True, toRequiresConversion = True):
        if timeFrom is None:
            timeFrom = "now"
            fromRequiresConversion = False

        if timeTo is None:
            timeTo = "now - 6h"
            toRequiresConversion = False

        self.timeFrom = timeFrom
        self.timeTo = timeTo
        self.fromRequiresConversion = fromRequiresConversion
        self.toRequiresConversion = toRequiresConversion

    def get_json_string(self):
        self.timeFrom = Time.convert_to_standard_format(self.timeFrom, self.fromRequiresConversion)
        self.timeTo = Time.convert_to_standard_format(self.timeTo, self.toRequiresConversion)
        return "\"from\": {},\"to\": {}".format(self.timeFrom, self.timeTo)