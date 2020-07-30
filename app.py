import os, json, datetime

import pysftp, paramiko

from stages import Stages
from data import Data
from helpers import Helpers
from profiles_history import ProfilesHistory

def main():
  os.system("clear")
  os.chdir(".")
  Data.default_cwd = os.getcwd()
  Data.logs = []
  Data.fails = []
  Data.PROFILES_HISTORY_DIR_PATH = (
    os.path.expanduser("~") + "/" +
    Data.PROFILES_HISTORY_DIR_PATH
  )

  # Getting deploy profiles from history
  deploy_profile = None
  is_hist_profile_selected = False
  if Data.USE_PROFILES_HISTORY_SEARCH:
    profiles_history = ProfilesHistory.get_profiles_paths_from_history()
    if len(profiles_history) > 0:
      print("[i] Found profiles in history:")
      print("0. Enter deploy profile path manually")
      profiles_history_counter = 0
      for one_hist_profile_path in profiles_history:
        profiles_history_counter = profiles_history_counter + 1
        print(str(profiles_history_counter) + ". " + one_hist_profile_path)
      print("Select variant:")
      selected_hist_profile_idx = input()
      try:
        selected_hist_profile_idx = int(selected_hist_profile_idx)
        if selected_hist_profile_idx > 0:
          is_hist_profile_selected = True
          deploy_profile = Helpers.get_profile_file(profiles_history[selected_hist_profile_idx-1])
      except:
        exit("[X] Invalid input!")
  if not is_hist_profile_selected:
    # Reading deploy profile manually
    deploy_profile = Helpers.get_profile_file(None)
    if deploy_profile == None or deploy_profile == False:
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
  deploy_credentials = deploy_profile["environments"][selected_profile_env]["credentials"]
  stages_counter = 0
  for one_stage in deploy_stages:
    if one_stage["ignore"]:
      print("[i] " + str(stages_counter) +  ". " + str(one_stage["name"]) + " (IGNORED)")
      continue
    stages_counter = stages_counter + 1
    print("[i] " + str(stages_counter) +  ". " + str(one_stage["print"]))
    result = Stages.run_stage(one_stage["name"], one_stage["details"], deploy_credentials)
    if result != True:
      print("[!] Current stage failed!\nResult:\n" + str(result) + "\nContinue? (yes/no)")
      continue_or_not = input()
      if continue_or_not.replace(" ", "") != "yes":
        exit("[X] Exited with error!")
  
  # Saving current profile path to local history
  ProfilesHistory.save_profile_path_to_history(Data.curr_profile_path)

  end_time = datetime.datetime.now()
  print("[i] All done in " + str(int((end_time-start_time).total_seconds())) + " seconds!")

main()