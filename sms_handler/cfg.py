import configparser

config = configparser.ConfigParser()


def write_dev_config(ini_file_path="../config.ini"):
    config["DATABASE"] = {"database_type": "sqlite",
                          "database_name": "database.db"}
    config["SMS_SERVICE"] = {"smsc_login": "yoki.ua",
                             "smsc_password": "2NBYbt9RyvT7D3&start=22.05.2022&end=22.05.2022&fmt=3&cnt=50"}
    with open(ini_file_path, "w") as file:
        config.write(file)


def read_config(ini_file_path="config.ini"):
    config.read(ini_file_path)


if __name__ == '__main__':
    write_dev_config()

read_config()
