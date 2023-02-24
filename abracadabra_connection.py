import subprocess


def run_python3_script(function_name, *args):
    # Path to the Python 3 interpreter for the virtual environment abracadabra and the path to the script to be run
    python_path = '/home/just/miniconda3/envs/abracadabra/bin/python'
    script_path = '/home/just/dev/uni/RoboCup/robo-dance/abracadabra/main.py'

    # Command to run the Python 3 script
    cmd = [python_path, script_path, function_name] + list(args)

    # Run the command and capture the output
    output = subprocess.check_output(cmd)

    # Decode the output from bytes to string
    result = output.decode('utf-8').strip()

    # Return the result
    return result


if __name__ == '__main__':
    # result = run_python3_script('setup')
    result = run_python3_script('list_songs')
    # result = run_python3_script('recognise', 'out2.wav')
    print(result)
