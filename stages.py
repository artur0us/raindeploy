import os
import subprocess
from typing import Union

import pysftp
import paramiko

from data import Data, DEBUG_MODE
from helpers import Helpers
from utils import print_logs


SSH_SHELL_CMD = 'ssh_shell_cmd'
LOCAL_SHELL_CMD = 'local_shell_cmd'
BUILD_GOLANG_PROJECT = 'build_golang_project'
SFTP_FILE_UPLOAD = 'sftp_file_upload'
SFTP_DIR_UPLOAD = 'sftp_dir_upload'


class Stages:

    @staticmethod
    def run_stage(stage_name: str, stage_details: dict, env_credentials: dict) -> Union[str, bool]:
        # Validation
        if not stage_name or stage_name.replace(' ', '') == "":
            return "invalid stage name"
        if not stage_details:
            return "invalid stage details"
        stage_name = stage_name.replace(" ", "")

        # Searching for needed method
        if stage_name == SSH_SHELL_CMD:
            result = Stages.ssh_shell_cmd(stage_name, stage_details, env_credentials)
        elif stage_name == LOCAL_SHELL_CMD:
            result = Stages.local_shell_cmd(stage_name, stage_details, env_credentials)
        elif stage_name == BUILD_GOLANG_PROJECT:
            result = Stages.build_golang_project(stage_name, stage_details, env_credentials)
        elif stage_name == SFTP_FILE_UPLOAD:
            result = Stages.sftp_file_upload(stage_name, stage_details, env_credentials)
        elif stage_name == SFTP_DIR_UPLOAD:
            result = Stages.sftp_dir_upload(stage_name, stage_details, env_credentials)
        else:
            result = "unknown stage name"

        return result

    @staticmethod
    def ssh_shell_cmd(stage_name: str, stage_details: dict, env_credentials: dict) -> Union[str, bool]:
        try:
            ssh_credentials = Helpers.get_env_credentials(env_credentials, "ssh", stage_details["ssh_config"])
            if not ssh_credentials:
                err_msg = "ssh credentials reading error"
                Data.fails.append(err_msg)
                return err_msg

            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(
                hostname=ssh_credentials["host"],
                port=ssh_credentials["port"],
                username=ssh_credentials["username"],
                password=ssh_credentials["password"]
            )
            try:
                cmd_stdin, cmd_stdout, cmd_stderr = ssh_client.exec_command(stage_details["cmd"], get_pty=True)
                # exit_status = cmd_stdout.channel.recv_exit_status()
                # if exit_status < 0:
                #   pass # TODO: return error message or not?
                data = cmd_stdout.read() + cmd_stderr.read()
                Data.logs.append(data)
                if Data.WORK_MODE == DEBUG_MODE:
                    print_logs(data)
                ssh_client.close()
            except Exception as err:
                err_msg = "(ssh_shell_cmd) command execution failed:\n" + str(err)
                Data.fails.append(err_msg)
                return err_msg
        except Exception as err:
            err_msg = "(ssh_shell_cmd) SSH connection failed:\n" + str(err)
            Data.fails.append(err_msg)
            return err_msg
        return True

    @staticmethod
    def local_shell_cmd(stage_name: str, stage_details: dict, env_credentials: dict) -> Union[str, bool]:
        try:
            proc = subprocess.Popen(stage_details["cmd"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            proc_out, proc_err = proc.communicate()
            Data.logs.append(proc_out)
            Data.logs.append(proc_err)
            if Data.WORK_MODE == DEBUG_MODE:
                print_logs(proc_out, proc_err)

        except Exception as err:
            err_msg = "(local_shell_cmd) command execution failed:\n" + str(err)
            Data.fails.append(err_msg)
            return err_msg
        return True

    @staticmethod
    def build_golang_project(stage_name: str, stage_details: dict, env_credentials: dict) -> Union[str, bool]:
        # Old built file removal
        try:
            os.remove(stage_details["paths"]["target_build_file"])
        except:
            pass

        # Compilation
        try:
            # Compile command preparation
            compile_command = ""
            for one_var in stage_details["build"]["variables"]:
                compile_command = compile_command + one_var + " "
            compile_command = (
                compile_command +
                "go build -o " +
                stage_details["paths"]["target_build_file"] +
                " " + stage_details["paths"]["main_src_file"]
            )
            if Data.WORK_MODE == DEBUG_MODE:
                print(compile_command)

            # Changing working directory to go sources path
            os.chdir(stage_details["paths"]["main_src"])

            # Compilation
            proc = subprocess.Popen(compile_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            proc_out, proc_err = proc.communicate()
            Data.logs.append(proc_out)
            Data.logs.append(proc_err)
            if Data.WORK_MODE == DEBUG_MODE:
                print_logs(proc_out, proc_err)
            if (
                ("error" in str(proc_out).lower())
                or ("error" in str(proc_err).lower())

                or ("undefined:" in str(proc_out).lower())
                or ("undefined:" in str(proc_err).lower())

                or ("cannot use" in str(proc_out).lower())
                or ("cannot use" in str(proc_err).lower())

                or ("not enough arguments" in str(proc_out).lower())
                or ("not enough arguments" in str(proc_err).lower())

                or ("is not in goroot" in str(proc_out).lower())
                or ("is not in goroot" in str(proc_err).lower())

                or ("invalid operation" in str(proc_out).lower())
                or ("invalid operation" in str(proc_err).lower())

                or ("does not support indexing" in str(proc_out).lower())
                or ("does not support indexing" in str(proc_err).lower())

                or ("invalid operation" in str(proc_out).lower())
                or ("invalid operation" in str(proc_err).lower())

                or ("want" in str(proc_out).lower())
                or ("want" in str(proc_err).lower())
                ):
                err_msg = "(build_golang_project) golang project source code compilation failed:\n" + str(
                    proc_out) + "\n" + str(proc_err)
                Data.fails.append(err_msg)
                return err_msg

            # chmod +x built_go_executable_file
            if stage_details["build"]["chmod_x_built_file"]:
                proc = None
                proc_out = None
                proc_err = None
                chmod_command = "chmod +x " + stage_details["paths"]["target_build_file"]
                proc = subprocess.Popen(chmod_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                proc_out, proc_err = proc.communicate()
                Data.logs.append(proc_out)
                Data.logs.append(proc_err)
                if Data.WORK_MODE == DEBUG_MODE:
                    print_logs(proc_out, proc_err)

            # Restore default working directory
            os.chdir(Data.default_cwd)
        except Exception as err:
            err_msg = "(build_golang_project) compiler command execution failed:\n" + str(err)
            Data.fails.append(err_msg)
            return err_msg
        return True

    @staticmethod
    def sftp_file_upload(stage_name: str, stage_details: dict, env_credentials: dict) -> Union[str, bool]:
        try:
            sftp_credentials = Helpers.get_env_credentials(env_credentials, "sftp", stage_details["sftp_config"])
            if not sftp_credentials:
                err_msg = "sftp credentials reading error"
                Data.fails.append(err_msg)
                return err_msg

            sftp_conn_options = pysftp.CnOpts()
            sftp_conn_options.hostkeys = None
            sftp_client = pysftp.Connection(
                sftp_credentials["host"],
                username=sftp_credentials["username"],
                password=sftp_credentials["password"],
                cnopts=sftp_conn_options
            )
            try:
                sftp_client.put(stage_details["file_local_path"], stage_details["file_dest_path"], preserve_mtime=True)
                sftp_client.close()
            except Exception as err:
                err_msg = "(sftp_file_upload) upload failed:\n" + str(err)
                Data.fails.append(err_msg)
                return err_msg
        except Exception as err:
            err_msg = "(sftp_file_upload) SFTP connection failed:\n" + str(err)
            Data.fails.append(err_msg)
            return err_msg
        return True

    @staticmethod
    def sftp_dir_upload(stage_name: str, stage_details: dict, env_credentials: dict) -> Union[str, bool]:
        try:
            sftp_credentials = Helpers.get_env_credentials(env_credentials, "sftp", stage_details["sftp_config"])
            if not sftp_credentials:
                err_msg = "sftp credentials reading error"
                Data.fails.append(err_msg)
                return err_msg
            sftp_client = {}
            sftp_conn_options = pysftp.CnOpts()
            sftp_conn_options.hostkeys = None
            sftp_client = pysftp.Connection(
                sftp_credentials["host"],
                username=sftp_credentials["username"],
                password=sftp_credentials["password"],
                cnopts=sftp_conn_options
            )
            try:
                sftp_client.put_r(stage_details["dir_local_path"], stage_details["dir_dest_path"], preserve_mtime=True)
                sftp_client.close()
            except Exception as err:
                err_msg = "(sftp_dir_upload) upload failed:\n" + str(err)
                Data.fails.append(err_msg)
                return err_msg
        except Exception as err:
            err_msg = "(sftp_dir_upload) SFTP connection failed:\n" + str(err)
            Data.fails.append(err_msg)
            return err_msg
        return True
