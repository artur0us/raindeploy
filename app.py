import os, json, datetime

import pysftp, paramiko

from stages import Stages
from data import Data
from helpers import Helpers

def main():
  os.system("clear")
  os.chdir(".")
  Data.default_cwd = os.getcwd()
  Data.logs = []
  Data.fails = []

  # Reading deploy profile
  deploy_profile = Helpers.get_profile_file()
  if deploy_profile == False:
    exit("[X] Invalid deploy profile or file not found!")

  start_time = datetime.datetime.now()

  # Profile validation
  profile_validation_res = Helpers.validate_profile(deploy_profile)
  if profile_validation_res != True:
    exit("[X] Profile validation error: " + str(profile_validation_res))
  
  # Parsing profile environments
  print("[i] Found environments: " + str(Helpers.get_all_profile_envs(deploy_profile)))
  selected_profile_env = Helpers.select_profile_env(deploy_profile)
  if selected_profile_env == False:
    exit("[X] Unknown environment!")
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
      continue_or_not = input()
      if continue_or_not.replace(" ", "") != "yes":
        exit("[X] Exited with error!")
  
  end_time = datetime.datetime.now()
  print("[i] All done in " + str(int((end_time-start_time).total_seconds())) + " seconds!")

main()