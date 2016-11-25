import pwd
import subprocess

if __name__ == '__main__':
    {% for username in currentDroplet.currentSetupStep.usernames %}
    try:
        pwd.getpwnam('{{ username }}')
        print 'user {0} exists'.format('{{ username }}')
    except KeyError:
        subprocess.check_call(['adduser','--disabled-password','--gecos', '""', '{{ username }}'])
    {% endfor %}    