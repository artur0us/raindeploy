import os, json, datetime, subprocess

import pysftp, paramiko

from data import Data
from helpers import Helpers

class Stages:

  @staticmethod
  def run_stage(stage_name, stage_details, env_credentials):
    # Validation
    if stage_name == None or stage_name.replace(" ", "") == "":
      return "invalid stage name"
    if stage_details == None:
      return "invalid stage details"
    stage_name = stage_name.replace(" ", "")

    result = "unknown error"

    # Searching for needed method
    if stage_name == "ssh_shell_cmd":
      result = Stages.ssh_shell_cmd(stage_name, stage_details, env_credentials)
    elif stage_name == "local_shell_cmd":
      result = Stages.local_shell_cmd(stage_name, stage_details, env_credentials)
    elif stage_name == "build_golang_project":
      result = Stages.build_golang_project(stage_name, stage_details, env_credentials)
    elif stage_name == "sftp_file_upload":
      result = Stages.sftp_file_upload(stage_name, stage_details, env_credentials)
    elif stage_name == "sftp_dir_upload":
      result = Stages.sftp_dir_upload(stage_name, stage_details, env_credentials)
    else:
      result = "unknown stage name"
    
    return result

  @staticmethod
  def ssh_shell_cmd(stage_name, stage_details, env_credentials):
    try:
      ssh_credentials = Helpers.get_env_credentials(env_credentials, "ssh", stage_details["ssh_config"])
      if ssh_credentials == False:
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
        if Data.WORK_MODE == "debug":
          print("=========================================")
          print(data)
          print("=========================================")
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
  def local_shell_cmd(stage_name, stage_details, env_credentials):
    try:
      # exec_msg = os.popen(stage_details["cmd"]).read()
      # Data.logs.append(exec_msg)
      # if Data.WORK_MODE == "debug":
      #   print("=========================================")
      #   print(exec_msg)
      #   print("=========================================")
      proc = subprocess.Popen(stage_details["cmd"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
      proc_out, proc_err = proc.communicate()
      Data.logs.append(proc_out)
      Data.logs.append(proc_err)
      if Data.WORK_MODE == "debug":
        print("=========================================")
        print(proc_out)
        print(proc_err)
        print("=========================================")
    except Exception as err:
      err_msg = "(local_shell_cmd) command execution failed:\n" + str(err)
      Data.fails.append(err_msg)
      return err_msg
    return True

  @staticmethod
  def build_golang_project(stage_name, stage_details, env_credentials):
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
      if Data.WORK_MODE == "debug":
        print(compile_command)

      # Changing working directory to go sources path
      os.chdir(stage_details["paths"]["main_src"])

      # Compilation
      # exec_msg = os.popen(compile_command).read()
      # Data.logs.append(exec_msg)
      # if Data.WORK_MODE == "debug":
      #   print("=========================================")
      #   print(exec_msg)
      #   print("=========================================")
      proc = subprocess.Popen(compile_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
      proc_out, proc_err = proc.communicate()
      Data.logs.append(proc_out)
      Data.logs.append(proc_err)
      if Data.WORK_MODE == "debug":
        print("=========================================")
        print(proc_out)
        print(proc_err)
        print("=========================================")
      if ("error" in str(proc_out).lower()) or ("error" in str(proc_err).lower()):
        err_msg = "(build_golang_project) golang project source code compilation failed:\n" + str(proc_out) + "\n" + str(proc_err)
        Data.fails.append(err_msg)
        return err_msg

      # chmod +x built_go_executable_file
      if stage_details["build"]["chmod_x_built_file"]:
        # os.popen("chmod +x " + stage_details["paths"]["target_build_file"]).read()
        proc = None
        proc_out = None
        proc_err = None
        chmod_command = "chmod +x " + stage_details["paths"]["target_build_file"]
        proc = subprocess.Popen(chmod_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        proc_out, proc_err = proc.communicate()
        Data.logs.append(proc_out)
        Data.logs.append(proc_err)
        if Data.WORK_MODE == "debug":
          print("=========================================")
          print(proc_out)
          print(proc_err)
          print("=========================================")
      
      # Restore default working directory
      os.chdir(Data.default_cwd)
    except Exception as err:
      err_msg = "(build_golang_project) compiler command execution failed:\n" + str(err)
      Data.fails.append(err_msg)
      return err_msg
    return True

  @staticmethod
  def sftp_file_upload(stage_name, stage_details, env_credentials):
    try:
      sftp_credentials = Helpers.get_env_credentials(env_credentials, "sftp", stage_details["sftp_config"])
      if sftp_credentials == False:
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
  def sftp_dir_upload(stage_name, stage_details, env_credentials):
    try:
      sftp_credentials = Helpers.get_env_credentials(env_credentials, "sftp", stage_details["sftp_config"])
      if sftp_credentials == False:
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