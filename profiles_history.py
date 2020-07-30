import os, json

from data import Data

class ProfilesHistory:

  @staticmethod
  def get_profiles_paths_from_history():
    profiles_paths_history = []

    try:
      # Full path to profiles history file
      profiles_history_file_path = (
        Data.PROFILES_HISTORY_DIR_PATH + "/" + Data.PROFILES_HISTORY_FILE_NAME
      )

      if os.path.exists(profiles_history_file_path):
        # Reading current history
        profiles_history_file = open(profiles_history_file_path, "r")
        profiles_history = profiles_history_file.read()
        profiles_history_file.close()
        profiles_history = json.loads(profiles_history)
        if type(profiles_history) == list:
          for one_hist_profile_path in profiles_history:
            if os.path.exists(one_hist_profile_path):
              profiles_paths_history.append(one_hist_profile_path)
    except Exception as err:
      print(err)
      pass

    return profiles_paths_history

  @staticmethod
  def save_profile_path_to_history(curr_profile_path):
    if curr_profile_path == None or type(curr_profile_path) != str:
      return False
    
    try:
      # Create directory if not exists
      if not os.path.exists(Data.PROFILES_HISTORY_DIR_PATH):
        os.makedirs(Data.PROFILES_HISTORY_DIR_PATH)
      
      # Full path to profiles history file
      profiles_history_file_path = (
        Data.PROFILES_HISTORY_DIR_PATH + "/" + Data.PROFILES_HISTORY_FILE_NAME
      )

      # Create profiles history file if not exists
      if not os.path.exists(profiles_history_file_path):
        tmp_file = open(profiles_history_file_path, "w")
        tmp_file.write("[]")
        tmp_file.close()
      
      # Reading current history
      profiles_history_file = open(profiles_history_file_path, "r")
      profiles_history = profiles_history_file.read()
      profiles_history_file.close()

      # Parsing profiles history as JSON array
      profiles_history = json.loads(profiles_history)
      is_curr_profile_path_added = False

      # Add current profile path only if it not already exists
      for one_hist_profile_path in profiles_history:
        if one_hist_profile_path == curr_profile_path:
          is_curr_profile_path_added = True
      if not is_curr_profile_path_added:
        profiles_history.append(curr_profile_path)
      
      # Saving profiles history
      profiles_history_file = open(profiles_history_file_path, "w")
      profiles_history_file.write(json.dumps(profiles_history))
      profiles_history_file.close()
    except Exception as err:
      print(err)
      return False
    
    return True