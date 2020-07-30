import os, json

from data import Data

class Helpers:

  @staticmethod
  def get_profile_file(hist_profile_path = None):
    deploy_profile_file = None
    deploy_profile_path = None
    if hist_profile_path == None or type(hist_profile_path) != str:
      print("[>] Enter deploy profile file path: ")
      deploy_profile_path = input() # sample_profile.json
      if not os.path.isfile(deploy_profile_path):
        # exit("[X] Deploy profile file not found!")
        return False
    else:
      deploy_profile_path = hist_profile_path
    
    if deploy_profile_path == None or type(deploy_profile_path) != str:
      return False

    try:
      deploy_profile_file = open(deploy_profile_path, "r")
    except:
      return False
    if deploy_profile_file == None:
      return False
    deploy_profile = None
    try:
      deploy_profile = json.loads(deploy_profile_file.read())
    except:
      # exit("[X] Invalid deploy profile!")
      deploy_profile_file.close()
      return False
    deploy_profile_file.close()
    Data.curr_profile_path = deploy_profile_path
    return deploy_profile

  @staticmethod
  def validate_profile(deploy_profile):
    try:
      if deploy_profile == None:
        return "profile is empty"
      if deploy_profile["signature"] != "raindeploy":
        return "wrong signature"
      if deploy_profile["environments"] == None:
        return "environments are empty"
      if deploy_profile["environments"] == None:
        return "environments are empty"
      if len(deploy_profile["environments"]) < 1:
        return "environments are empty"
      for env_name in deploy_profile["environments"]:
        if deploy_profile["environments"][env_name] == None:
          return "*" + env_name + "* environment is empty"
        if len(deploy_profile["environments"][env_name]) < 1:
          return "*" + env_name + "* environment is empty"
        if deploy_profile["environments"][env_name]["stages"] == None:
          return "*" + env_name + "* stages array is empty"
        if len(deploy_profile["environments"][env_name]["stages"]) < 1:
          return "*" + env_name + "* stages array is empty"
        
        # TODO: check environment credentials

        stages_counter = 0
        for one_stage in deploy_profile["environments"][env_name]["stages"]:
          stages_counter = stages_counter + 1
          if one_stage["name"] == None:
            return "*" + env_name + "* stage #" + str(stages_counter) + " (unknown) is null"
          if len(one_stage["name"]) < 1:
            return "*" + env_name + "* stage #" + str(stages_counter) + " (unknown) is empty"
          if one_stage["print"] == None:
            return "*" + env_name + "* stage #" + str(stages_counter) + " (" + str(one_stage["name"]) + ") printing msg is null"
          if len(one_stage["print"]) < 1:
            return "*" + env_name + "* stage #" + str(stages_counter) + " (" + str(one_stage["name"]) + ") printing msg is empty"
          if one_stage["details"] == None:
            return "*" + env_name + "* stage #" + str(stages_counter) + " (" + str(one_stage["name"]) + ") details are null"
          
          # TODO: check stage details for every stage variant

          if one_stage["ignore"] == None:
            return "*" + env_name + "* stage #" + str(stages_counter) + " (" + str(one_stage["name"]) + ") ignore field is null"
    except Exception as err:
      return "some fields not found, details: " + str(err)
    
    return True
  
  @staticmethod
  def get_all_profile_envs(deploy_profile):
    found_envs = []
    for env_name in deploy_profile["environments"]:
      found_envs.append(env_name)
    return found_envs
  
  @staticmethod
  def select_profile_env(deploy_profile):
    if len(deploy_profile["environments"]) > 1:
      print("[>] Enter needed environment:")
      entered_profile_env = input()
      try:
        if deploy_profile["environments"][entered_profile_env] == None:
          return False
      except:
        return False
      return entered_profile_env
    else:
      for env_name in deploy_profile["environments"]:
        return env_name
  
  @staticmethod
  def get_env_credentials(credentials, svc_name, svc_user):
    try:
      if credentials[svc_name][svc_user] == None:
        return False
    except:
      return False
    return credentials[svc_name][svc_user]