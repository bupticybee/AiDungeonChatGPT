from config import config
# from app import ChatApplication
from utils import print_logo, print_warp, error, input_option
from colorama import Fore

PYCHATGPT_AVAILABLE = True
try:
    from revChatGPT.V1 import Chatbot
    from revChatGPT.V3 import Chatbot as ofChatbot
except:
    print("Your Python version is lower than 3.9 or does not have pychatgpt installed, and you cannot use the login "
          "function. The default token will be used instead.\n\n\n")
    PYCHATGPT_AVAILABLE = False


class StoryTeller:
    def __init__(self, background):
        """
        Setup chatbot based on type and config.
        Config has different format base on type.
        if type = 0:
            config = {
                "session_token": str,
            }
        if type = 1:
            config = {
                "email": str,
                "password": str,
            }
        """
        self.background = background
        self.type = None  # 0 for api token (official api) or 1 for openai account (free api)
        self.config = None
        self.chatbot = None
        self.first_interact = True

    def login(self, _config):
        if self.type == 0:
            self.chatbot = ofChatbot(api_key=_config['api_key'])
        else:
            self.chatbot = Chatbot(_config)

    def config_by_token(self):
        """
        Config by api token (official api)
        """
        self.type = 0

        api_key = input("Please input api_key(get it from: https://platform.openai.com/account/api-keys):")
        _config = {'api_key': api_key}
        return _config

    def config_by_account(self):
        """
        Config by Openai account
        """
        _config = {
            "email": "",
            "password": "",
            # "conversation_id": "",
            # "parent_id": "",
            # "proxy": "",
            "paid": False
        }
        self.type = 1
        print("Please enter OpenAI account email and password:")
        _config["email"] = input("email:")
        _config["password"] = input("password:")
        prox = input("To use a proxy, enter the proxy url. If not, press Enter directly.")
        if prox:
            _config["proxy"] = prox

        paid = input_option("Are you a paying user?", 'y', 'n', 'n')
        if paid:
            _config["paid"] = True
        try:
            with open('id_log.txt', 'r') as f:
                lines = f.readlines()
                last_line = lines[-1]
                if last_line:
                    resume = input_option("Discover previous adventures. Whether to continue the adventure:", 'y', 'n', 'y')
                    if resume:
                        self.first_interact = False
                        _config["parent_id"] = last_line
        except:
            pass

        return _config

    def setup_chatbot(self):
        self.config = self.get_config()
        self.login(self.config)

        if self.first_interact:
            print("Please enter a background story. Leave blank to use the default background story.")
            background = input()
            if background:
                self.background = background
        else:
            try:
                with open('chat_log.txt', 'r') as f:
                    lines = f.readlines()
                    last_line = lines[-1]
                    if last_line:
                        self.background = last_line
            except:
                self.background = ""
        print("\n\n\n")

    def get_config(self):
        if PYCHATGPT_AVAILABLE:
            print("Please choose how to login：\n y:Use the reverse engineering api.\n    " + Fore.RED + "~Account may be banned! use with caution.\n" + Fore.RESET + "    ~Free, requires an OpenAI account. \n n:Use official APIs.\n    "
                  "~Account needs to be opened for payment \n    ~Login with api key")
            res = input()
            if res == 'y':
                return self.config_by_account()
            else:
                return self.config_by_token()
        else:
            self.type = 0
            return config
        # return self.config_by_account()

    def start_cli(self):
        print_logo()
        self.setup_chatbot()
        self.interactive()

    # def start_app(self):
    #     app = ChatApplication(self.background)
    #     app.run()

    def save_conversation_id(self, conv_id):
        with open('id_log.txt', 'w') as f:
            f.writelines(conv_id)

    def save_conversations(self, res):
        with open('chat_log.txt', 'w') as f:
            f.writelines(res)

    def action(self, user_action):
        if user_action[-1] != "。":
            user_action = user_action + "。"
        if self.first_interact:
            prompt = """Now act as an adventure word game. When describing, pay attention to the rhythm, 
            not too fast, and carefully describe the mood and surrounding environment of each character. Write only 
            four to six sentences at a time. Start with,""" + self.story + """ You""" + user_action
        else:
            prompt = """Continue. You only need to continue writing four to six sentences at a time, and only talk 
            about what happened within 5 minutes. You""" + user_action
        response = ""

        if self.type == 1:
            for data in self.chatbot.ask(
                prompt
            ):
                response = data["message"]
            self.save_conversations(response)
            if self.first_interact:
                self.first_interact = False
                self.save_conversation_id(self.chatbot.get_conversations()[0]['id'])
        else:
            response = self.chatbot.ask(prompt)
        return response

    def interactive(self):
        # os.system('clear')
        print_warp(self.background)
        while True:
            action = input(Fore.GREEN + "> You")
            print_warp(self.action(action))
