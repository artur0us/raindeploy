import slack
from slack.errors import SlackApiError

from data import Data, DEBUG_MODE


class Notifications:

    @staticmethod
    def send_msg_to_slack(slack_token: str, channel_name: str, text: str, icon_emoji: str = ":heavy_check_mark:"):
        try:
            client = slack.WebClient(token=slack_token)
            response = client.chat_postMessage(
                channel="#" + channel_name,
                text=text,
                icon_emoji=icon_emoji
            )

            Data.logs.append(str(response))

            if Data.WORK_MODE == DEBUG_MODE:
                print(str(response))

        except SlackApiError as err:
            Data.fails.append(str(err.response['ok']))
            Data.fails.append(str(err.response['error']))

            if Data.WORK_MODE == DEBUG_MODE:
                print(str(err.response['ok']))
                print(str(err.response['error']))

        return True

    @staticmethod
    def validate_slack_bot_credentials(credentials: dict):
        if not credentials:
            return False
        if not credentials.get("slack_bot"):
            return False
        if credentials["slack_bot"].get("main"):
            return False
        if not credentials["slack_bot"]["main"].get("project_channel") or \
                type(credentials["slack_bot"]["main"]["project_channel"]) != str:
            return False
        if not credentials["slack_bot"]["main"].get("bot_token") or \
                type(credentials["slack_bot"]["main"]["bot_token"]) != str:
            return False

        return True
