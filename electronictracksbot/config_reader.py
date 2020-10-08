import configparser

class ConfigReader:

    def __init__(self):
        self._config_parser = configparser.ConfigParser()
        self._conf_values = {}
        self._load_file()

    def _load_file(self):
        self._config_parser.read_file(open('conf/config.cfg'))
        for section in self._config_parser.sections():
            for key in self._config_parser[section]:
                self._conf_values[(section, key)] = self._config_parser[section][key]

    def get(self, section, key):
        return self._conf_values.get((section, key))

