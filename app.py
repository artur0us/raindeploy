import os, json, datetime

import pysftp, paramiko

from stages import Stages
from data import Data

def main():
  os.system('clear')
  os.chdir(".")
  Data.default_cwd = os.getcwd()
  Data.fails = []

  # Reading profile
  print("[>] Enter deploy profile file path: ")
  deploy_profile_path = input() # sample_profile.json
  if not os.path.isfile(deploy_profile_path):
    exit("[X] Deploy profile file not found!")
  deploy_profile_file = open(deploy_profile_path, "r")
  deploy_profile = None
  try:
    deploy_profile = json.loads(deploy_profile_file.read())
  except:
    exit("[X] Invalid deploy profile!")
  deploy_profile_file.close()

  start_time = datetime.datetime.now()

  # Profile basic validation
  found_profile_envs = []
  try:
    if deploy_profile == None or deploy_profile["signature"] != "raindeploy":
      exit("[X] Invalid profile signature!")
    if deploy_profile["environments"] == None:
      exit("[X] No environments!")
    is_one_env_found = False
    for env_name in deploy_profile["environments"]:
      is_one_env_found = True
      found_profile_envs.append(env_name)
    if not is_one_env_found:
      exit("[X] No environments!")
  except:
    exit("[X] Invalid deploy profile!")
  
  # Parsing profile
  print("[i] Found environments: " + str(found_profile_envs))
  selected_profile_env = None
  if len(found_profile_envs) > 1:
    print("[>] Enter needed environment:")
    entered_profile_env = input()
    try:
      if deploy_profile["environments"][entered_profile_env] == None:
        exit("[X] Empty environment!")
    except:
      exit("[X] Unknown environment!")
    selected_profile_env = entered_profile_env
  else:
    selected_profile_env = found_profile_envs[0]
  try:
    if deploy_profile["environments"][selected_profile_env]["stages"] == None:
      exit("[X] No stages!")
    if len(deploy_profile["environments"][selected_profile_env]["stages"]) < 1:
      exit("[X] No stages!")
  except:
    exit("[X] No stages!")
  print("[i] Selected environment: " + selected_profile_env)

  # Processing stages
  print("[i] Processing stages...")
  deploy_stages = deploy_profile["environments"][selected_profile_env]["stages"]
  stages_counter = 0
  for one_stage in deploy_stages:
    if one_stage["ignore"]:
      print("[i] " + str(stages_counter) +  ". " + str(one_stage["name"]) + " (IGNORED)")
      continue
    stages_counter = stages_counter + 1
    print("[i] " + str(stages_counter) +  ". " + str(one_stage["print"]))
    result = Stages.run_stage(one_stage["name"], one_stage["details"])
    if result != True:
      print("[!] Current stage failed!\nResult:\n" + str(result) + "\nContinue? (yes/no)")
      continue_input = input()
      if continue_input.replace(" ", "") != "yes":
        exit("[X] Exited with error!")
  
  end_time = datetime.datetime.now()
  print("[i] All done in " + str(int((end_time-start_time).total_seconds())) + " seconds!")

main()