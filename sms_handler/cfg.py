import configparser

INI_FILE_PATH = "config.ini"

config = configparser.ConfigParser()

config.read(INI_FILE_PATH)
