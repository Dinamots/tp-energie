import configparser


class Utils:

    @staticmethod
    def flatten(S):
        if not S:
            return S
        if isinstance(S[0], list):
            return Utils.flatten(S[0]) + Utils.flatten(S[1:])
        return S[:1] + Utils.flatten(S[1:])

    @staticmethod
    def getSection(filePath, sectionName):
        config = configparser.ConfigParser()
        config.read(filePath)
        return config[sectionName]
