import subprocess

if __name__ == '__main__':
    {% for package in currentDroplet.currentSetupStep.packages %}
    subprocess.check_call(['pip','install', '{{ package }}'])
    {% endfor %}
