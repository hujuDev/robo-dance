import os
import subprocess


class PythonRunner:
    def __init__(self, python_path, script_path):
        self.python_path = python_path
        self.script_path = script_path

    def run_script(self, function_name, *args):
        # Command to run the Python 3 script
        cmd = [self.python_path, self.script_path, function_name] + list(args)

        # Run the command and capture the output
        output = subprocess.check_output(cmd)

        # Decode the output from bytes to string
        result = output.decode('utf-8').strip()

        # Return the result
        return result

    def recognize_from_file(self):
        result = self.run_script('recognise', 'out.wav').splitlines()
        result = {
            'song_name': result[0].encode('ascii', 'replace'),
            'score': result[1].encode('ascii', 'replace')
        }
        return result

if __name__ == '__main__':
    python_path = '/home/just/miniconda3/envs/abracadabra/bin/python'
    script_path = 'abracadabra/python2_interface.py'
    runner = PythonRunner(python_path, script_path)

    # result = runner.run_script('resetup')
    # result = runner.run_script('setup')
    # result = runner.run_script('list_songs')
    # result = runner.run_script('recognise', 'out.wav').splitlines()
    result = runner.recognize_from_file()

    print(result)
