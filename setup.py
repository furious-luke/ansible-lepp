#!/usr/bin/env python

# Point to where you placed ansible-lepp.
PLAYBOOK_PATH = 'config'

import os, sys, subprocess, argparse

def run(cmd, output=False):
    if output:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    else:
        subprocess.check_call(cmd, shell=True)

def check_ansible_version():
    try:
        output = run('ansible-playbook --version', True)
        ver = int(output.splitlines()[0].split()[1].decode().split('.')[0])
    except:
        sys.stdout.write('Unable to locate Ansible.\n')
        ver = 0
    if ver < 2:
        sys.stdout.write('Please use Ansible 2.0.0 or above.\n')
        sys.stdout.write('\n')
        sys.stdout.write('To install latest Ansible:\n')
        sys.stdout.write(' git clone --recursive git://github.com/ansible/ansible.git ansible-git\n')
        sys.stdout.write(' cd ansible-git\n')
        sys.stdout.write(' sudo python setup.py install\n')
        sys.stdout.write('\n')
        sys.exit(1)

def check_ansible_python():
    okay = True
    try:
        import ansible.modules.core.packaging.language as tmp
    except:
        sys.stdout.write('Unable to import Ansible.\n')
        okay = False
    if okay:
        with open(os.path.join(os.path.dirname(tmp.__file__), 'pip.py')) as file:
            contents = file.read()
        if 'virtualenv_python' not in contents:
            sys.stdout.write('Ansible 2.0.0 detected, but incompatible `pip` module found.\n')
            okay = False
    if not okay:
        sys.stdout.write('This usually happens as a result of installing Ansible under\n')
        sys.stdout.write('one Python installation, but then running `setup.py` with another.\n')
        sys.stdout.write('Please be sure to run:\n')
        sys.stdout.write('  ./setup.py\n')
        sys.stdout.write('without directly specifying a Python interpreter, or be sure the\n')
        sys.stdout.write('Python intepreter you specify is the same one Ansible was installed\n')
        sys.stdout.write('under.\n')
        sys.exit(1)

def parse_arguments():
    parser = argparse.ArgumentParser('Setup Django Python environment.')
    parser.add_argument('--deploy', '-d', choices=['development', 'production'], default='development',
                        help='deployment type')
    parser.add_argument('--disable-become', action='store_true', help='disable promotion')
    args = parser.parse_args()
    args.deploy = args.deploy.lower()
    return args

if __name__ == '__main__':
    check_ansible_version()
    check_ansible_python()
    args = parse_arguments()

    hosts = os.path.join(os.getcwd(), 'hosts')
    become = ' --ask-become' if (not args.disable_become) else ''
    os.chdir(PLAYBOOK_PATH)
    run('ansible-playbook -i %s -l %s site.yml%s'%(hosts, args.deploy, become))
