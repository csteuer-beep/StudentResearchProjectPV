# bash_command_handler.py

import subprocess

def execute_bash_command(comm, message):
    process = subprocess.Popen(comm, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.stdin.write(message.encode())
    process.stdin.flush()
    process.stdin.close()
    # Return the output and error if any
    # output, error = process.communicate()
    # return output.decode(), error.decode()
