import os, json
from typing import Union

from data import Data


class Helpers:

    @staticmethod
    def get_profile_file(hist_profile_path: str = None) -> Union[dict, bool]:
        if hist_profile_path is None or type(hist_profile_path) != str:
            deploy_profile_path = input("[>] Enter deploy profile file path: ")  # sample_profile.json
            if not os.path.isfile(deploy_profile_path):
                # exit("[X] Deploy profile file not found!")
                return False
        else:
            deploy_profile_path = hist_profile_path

        if deploy_profile_path is None or type(deploy_profile_path) != str:
            return False

        try:
            with open(deploy_profile_path, 'r') as deploy_profile_file:
                deploy_profile = json.loads(deploy_profile_file.read())
                Data.curr_profile_path = deploy_profile_path
                return deploy_profile
        except:
            # exit("[X] Invalid deploy profile!")
            return False

    @staticmethod
    def validate_profile(deploy_profile: dict) -> Union[str, bool]:
        try:
            if deploy_profile is None:
                return "profile is empty"
            if deploy_profile.get("signature") != "raindeploy":
                return "wrong signature"
            if deploy_profile.get("project_name") is None or not isinstance(deploy_profile["project_name"], str):
                return "invalid project name"
            if deploy_profile.get("environments") is None:
                return "environments are empty"
            if not deploy_profile.get("environments"):
                return "environments are empty"
            for env_name in deploy_profile["environments"]:
                if not deploy_profile["environments"][env_name]:
                    return "*" + env_name + "* environment is empty"
                if not deploy_profile["environments"][env_name].get("stages"):
                    return "*" + env_name + "* stages array is empty"

                # TODO: check environment credentials

                stages_counter = 0
                for one_stage in deploy_profile["environments"][env_name]["stages"]:
                    stages_counter = stages_counter + 1
                    if not one_stage.get("name"):
                        return "*" + env_name + "* stage #" + str(stages_counter) + " (unknown) is null"
                    if not one_stage["print"]:
                        return "*" + env_name + "* stage #" + str(stages_counter) + " (" + str(
                            one_stage["name"]) + ") printing msg is null"
                    if one_stage["details"] is None:
                        return "*" + env_name + "* stage #" + str(stages_counter) + " (" + str(
                            one_stage["name"]) + ") details are null"

                    # TODO: check stage details for every stage variant

                    if one_stage["ignore"] is None:
                        return "*" + env_name + "* stage #" + str(stages_counter) + " (" + str(
                            one_stage["name"]) + ") ignore field is null"
        except Exception as err:
            return "some fields not found, details: " + str(err)

        return True

    @staticmethod
    def get_all_profile_envs(deploy_profile: dict):
        return [env_name for env_name in deploy_profile['environments']]

    @staticmethod
    def select_profile_env(deploy_profile: dict) -> Union[str, bool]:
        if len(deploy_profile["environments"]) > 1:
            entered_profile_env = input('[>] Enter needed environment:')
            if deploy_profile['environments'].get(entered_profile_env) is None:
                return False
            return entered_profile_env
        else:
            for env_name in deploy_profile["environments"]:
                return env_name

    @staticmethod
    def get_env_credentials(credentials: dict, svc_name: str, svc_profile: str) -> Union[dict, bool]:
        if credentials and credentials.get(svc_name) and credentials[svc_name].get(svc_profile):
            return credentials[svc_name][svc_profile]
        return False
