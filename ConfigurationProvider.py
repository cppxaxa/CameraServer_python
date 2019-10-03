import json

class ConfigurationProvider:
    @staticmethod

    def getConfiguration(configFilePath):
        with open(configFilePath) as configFile:
            content = configFile.read()
            res = json.loads(content)

            return res