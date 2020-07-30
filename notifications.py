import slack
# from slack.errors import SlackApiError

class Notifications:

  @staticmethod
  def send_msg_to_slack(slack_token, channel_name, text, icon_emoji = ":heavy_check_mark:"):
    try:
      client = slack.WebClient(token=slack_token)
      response = client.chat_postMessage(
        channel = "#" + channel_name,
        text = text,
        icon_emoji = icon_emoji
      )
      # print(str(response))
    except Exception as err:
      # print(str(err))
      return False
    # except SlackApiError as err:
    #   print(str(err.response['ok']))
    #   print(str(err.response['error']))
    return True
  
  @staticmethod
  def validate_slack_bot_credentials(credentials):
    try:
      if credentials == None or credentials == False:
        return False
      if credentials["slack_bot"] == None or credentials["slack_bot"] == False:
        return False
      if credentials["slack_bot"]["main"] == None or credentials["slack_bot"]["main"] == False:
        return False
      if credentials["slack_bot"]["main"]["project_channel"] == None or type(credentials["slack_bot"]["main"]["project_channel"]) != str:
        return False
      if credentials["slack_bot"]["main"]["bot_token"] == None or type(credentials["slack_bot"]["main"]["bot_token"]) != str:
        return False
    except:
      return False
    return True