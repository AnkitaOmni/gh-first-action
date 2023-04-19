from dotenv import load_dotenv, find_dotenv, dotenv_values


class Config:
    """ # Fetch Config Details From (.env) file # """

    def get_config_json(self):
        # print(f"Dot Env File Path = {find_dotenv('.env')}")
        __config = None
        if load_dotenv(dotenv_path=find_dotenv('.env')):
            # print(f"Load Dot Env = {load_dotenv(dotenv_path=find_dotenv('.env'))}")
            __config = {
                **dotenv_values(".env"),  # load shared development variables
            }
            # print(f"Config = {config}")
        else:
            print("DotEnv File Not Found")
            __config = {"message": "DotEnv File Not Found"}

        return __config


if __name__ == '__main__':
    conf = Config()
    print(f"Raw Config = \n{conf.get_config_json()}\n\n")
    for eachItem in conf.get_config_json().items():
        print(eachItem)
    del conf, eachItem
