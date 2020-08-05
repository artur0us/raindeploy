from typing import Union


def print_logs(*args: Union[str, bytes]) -> None:
    if len(args) == 1:
        _print_log_data(args[0])
    elif len(args) == 2:
        _print_log_procs(*args)
    else:
        print('[X] Print logs error')


def _print_log_procs(proc_out: bytes, proc_err: bytes) -> None:
    print("=========================================")
    print(proc_out)
    print(proc_err)
    print("=========================================")


def _print_log_data(data: str) -> None:
    print("=========================================")
    print(data)
    print("=========================================")
