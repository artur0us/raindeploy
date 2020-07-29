import os, json, datetime

import pysftp, paramiko

from data import Data

class Stages:

  @staticmethod
  def run_stage(stage_name, stage_details):
    # Validation
    if stage_name == None or stage_name.replace(" ", "") == "":
      return "invalid stage name"
    if stage_details == None:
      return "invalid stage details"
    stage_name = stage_name.replace(" ", "")

    result = "unknown error"

    # Searching for needed method
    if stage_name == "ssh_shell_cmd":
      result = Stages.ssh_shell_cmd(stage_name, stage_details)
    elif stage_name == "local_shell_cmd":
      result = Stages.local_shell_cmd(stage_name, stage_details)
    elif stage_name == "build_golang_project":
      result = Stages.build_golang_project(stage_name, stage_details)
    elif stage_name == "sftp_file_upload":
      result = Stages.sftp_file_upload(stage_name, stage_details)
    else:
      result = "unknown stage name"
    
    return result

  @staticmethod
  def ssh_shell_cmd(stage_name, stage_details):
    try:
      ssh_client = paramiko.SSHClient()
      ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      ssh_client.connect(
        hostname=stage_details["ssh_host"],
        port=stage_details["ssh_port"],
        username=stage_details["ssh_username"],
        password=stage_details["ssh_password"]
      )
      try:
        cmd_stdin, cmd_stdout, cmd_stderr = ssh_client.exec_command(stage_details["cmd"], get_pty=True)
        # exit_status = cmd_stdout.channel.recv_exit_status()
        # if exit_status < 0:
        #   pass # TODO: return error message or not?
        data = cmd_stdout.read() + cmd_stderr.read()
        Data.logs.append(data)
        if Data.work_mode == "debug":
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
  def local_shell_cmd(stage_name, stage_details):
    try:
      exec_msg = os.popen(stage_details["cmd"]).read()
      Data.logs.append(exec_msg)
      if Data.work_mode == "debug":
        print("=========================================")
        print(exec_msg)
        print("=========================================")
    except Exception as err:
      err_msg = "(local_shell_cmd) command execution failed:\n" + str(err)
      Data.fails.append(err_msg)
      return err_msg
    return True

  @staticmethod
  def build_golang_project(stage_name, stage_details):
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

      # Changing working directory to go sources path
      os.chdir(stage_details["paths"]["main_src"])

      # Compilation
      if Data.work_mode == "debug":
        print(compile_command)
      exec_msg = os.popen(compile_command).read()
      Data.logs.append(exec_msg)
      if Data.work_mode == "debug":
        print("=========================================")
        print(exec_msg)
        print("=========================================")

      # chmod +x built_go_executable_file
      if stage_details["build"]["chmod_x_built_file"]:
        os.popen("chmod +x " + stage_details["paths"]["target_build_file"]).read()
      
      # Restore default working directory
      os.chdir(Data.default_cwd)
    except Exception as err:
      err_msg = "(build_golang_project) compiler command execution failed:\n" + str(err)
      Data.fails.append(err_msg)
      return err_msg
    return True

  @staticmethod
  def sftp_file_upload(stage_name, stage_details):
    try:
      sftp_client = {}
      sftp_conn_options = pysftp.CnOpts()
      sftp_conn_options.hostkeys = None
      sftp_client = pysftp.Connection(
        stage_details["sftp_host"],
        username=stage_details["sftp_username"],
        password=stage_details["sftp_password"],
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