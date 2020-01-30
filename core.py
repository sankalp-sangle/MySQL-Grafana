class Dashboard:
    def __init__(self, panels = None, properties = None):
        if properties is None:
            properties = Dashboard_Properties()
        if panels is None:
            panels = [Panel(title="Sample Panel")]

        self.properties          = properties
        self.panels              = panels
        self.json_representation = ""

    def get_json_string(self):
        panelJSON = self.get_colective_panels_json()
        return "{}, \"panels\":[{}]".format(self.properties.get_json_string(), panelJSON)

    def get_colective_panels_json(self):
        if self.panels is []:
            return ""
            
        panelJSON = ""
        for panel in self.panels:
            panelJSON += "{" + panel.get_json_string() + "},"

        #Remove trailing comma
        panelJSON = panelJSON[:-1]
        
        return panelJSON

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

class Grid_Position:
    
    DEFAULT_HEIGHT = 8
    DEFAULT_WIDTH = 12

    def __init__(self, x = None, y = None, height = None, width = None):
        if x is None:
            x = 0
        if y is None:
            y = 0
        if height is None:
            height = Grid_Position.DEFAULT_HEIGHT
        if width is None:
            width = Grid_Position.DEFAULT_WIDTH

        self.x = x
        self.y = y
        self.height = height
        self.width = width

    def get_json_string(self):
        return "\"h\": {}, \"w\": {}, \"x\": {}, \"y\": {}".format(self.height, self.width, self.x, self.y) 

class Panel:

    GLOBAL_ID = 1

    def __init__(self, datasource = None, id = None, title = None, panelType = None, gridPos = None):
        if datasource is None:
            datasource = "MySQL"
        if id is None:
            id = str(Panel.GLOBAL_ID)
            Panel.GLOBAL_ID += 1
        if title is None:
            title = "This is my sample panel title!"
        if panelType is None:
            panelType = "graph"
        if gridPos is None:
            gridPos = Grid_Position()

        self.datasource = datasource
        self.id = id
        self.title = title
        self.panelType = panelType
        self.gridPos = gridPos

    def get_json_string(self):
        return "\"datasource\": \"{}\",\"id\": {},\"title\": \"{}\",\"type\":\"{}\",\"gridPos\":{}".format(self.datasource, self.id, self.title, self.panelType, "{" + self.gridPos.get_json_string() + "}")

class Target:

    DEFAULT_FORMAT = "time_series"
    DEFAULT_RAW_SQL = ""
    DEFAULT_REFID = "A"

    def __init__(self, format = None, rawQuery = None, rawSql = None, refId = None):
        if format is None:
            format = Target.DEFAULT_FORMAT
        if rawQuery is None:
            rawQuery = True
        if rawSql is None:
            rawSql = Target.DEFAULT_RAW_SQL
        if refId is None:
            refId = Target.DEFAULT_REFID

        self.format = format
        self.rawQuery = rawQuery
        self.rawSql = rawSql
        self.refId = refId

    def get_json_string(self):
        pass

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