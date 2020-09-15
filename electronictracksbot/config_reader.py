import configparser

class ConfigReader:

    def __init__(self):
        self.__config_parser = configparser.ConfigParser()
        self.__conf_values = {}
        self.__load_file()

    def __load_file(self):
        self.__config_parser.read_file(open('conf/config.cfg'))
        for section in self.__config_parser.sections():
            for key in self.__config_parser[section]:
                self.__conf_values[(section, key)] = self.__config_parser[section][key]

    def get(self, section, key):
        return self.__conf_values.get((section, key))

