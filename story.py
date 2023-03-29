from revChatGPT.revChatGPT import Chatbot
try:
    from pychatgpt import OpenAI
except:
    print("Your Python version is lower than 3.9 or does not have pychatgpt installed, and you cannot use the login "
          "function. The default token will be used instead.\n\n\n")
import textwrap


def print_warp(instr):
    for i in textwrap.wrap(instr, width=50):
        print(i)


def login(config):
    expired_creds = OpenAI.token_expired()
    # expired_creds = True

    if expired_creds:
        print_warp("access_token has expired. Please choose to log in (y) or use the default session_token(n)。 Please "
                   "enter (y/n):")
        _input = input()
        if _input == 'y':
            email = input("email：")
            pwd = input("passward：")
            open_ai_auth = OpenAI.Auth(email_address=email, password=pwd)
            try:
                open_ai_auth.create_token()
            except:
                print_warp("Login failed! Please check your email and password. Default session_token will be used.")
                print("\n\n\n")
                return config
            else:
                access_token = OpenAI.get_access_token()
                config = {"Authorization": access_token[0]}
                print("\n\n\n")
                return config
        else:
            print("\n\n\n")
            return config
    else:
        access_token = OpenAI.get_access_token()
        config = {"Authorization": access_token[0]}
        return config



class StoryTeller():
    def __init__(self, config, story):
        self.chatbot = Chatbot(config, conversation_id=None)
        self.chatbot.reset_chat()  # Forgets conversation
        self.chatbot.refresh_session()  # Uses the session_token to get a new bearer token
        self.first_interact = True
        self.story = story

    def reset(self):
        self.chatbot.reset_chat()
        self.first_interact = True

    def action(self, user_action):
        if user_action[-1] != "。":
            user_action = user_action + "。"
        if self.first_interact:
            prompt = """Now act as an adventure word game. When describing, pay attention to the rhythm, 
            not too fast, and carefully describe the mood and surrounding environment of each character. Write only 
            four to six sentences at a time. Start with,""" + self.story + """ You""" + user_action
            self.first_interact = False
        else:
            prompt = """Continue. You only need to continue writing four to six sentences at a time, and only talk 
            about what happened within 5 minutes. You""" + user_action
        resp = self.chatbot.get_chat_response(prompt)  # Sends a request to the API and returns the response by OpenAI
        self.response = resp["message"]

    def interactive(self):
        print_warp(self.story)
        while True:
            action = input("> You")
            self.action(action)
            print_warp(self.response)
