class Data:

  # Consts
  USE_PROFILES_HISTORY_SEARCH = True
  PROFILES_HISTORY_DIR_PATH = ".raindeploy/profiles"
  PROFILES_HISTORY_FILE_NAME = "all.json"
  WORK_MODE = "quiet" # quiet/debug

  default_cwd = None
  curr_profile_path = None

  # Fails/logs messages
  fails = []
  logs = []