#!/usr/bin/env python

# Point to where you placed ansible-lepp.
PLAYBOOK_PATH = 'config'

import os, sys, subprocess, argparse

# def check_python_version():
#     if sys.version_info[0] < 3:
#         print('Please use Python 3 or above.')
#         sys.exit(1)
# check_python_version()

def run(cmd, output=False):
    if output:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    else:
        subprocess.check_call(cmd, shell=True)

def check_ansible_version():
    output = run('ansible-playbook --version', True)
    try:
        ver = int(output.splitlines()[0].split()[1].decode().split('.')[0])
    except:
        sys.stdout.write('Unable to locate ansible.\n')
        ver = 0
    if ver < 2:
        sys.stdout.write('Please use ansible 2.0.0 or above.\n')
        sys.stdout.write('\n')
        sys.stdout.write('To install latest ansible:\n')
        sys.stdout.write(' git clone --recursive git://github.com/ansible/ansible.git ansible-git\n')
        sys.stdout.write(' cd ansible-git\n')
        sys.stdout.write(' sudo python setup.py install\n')
        sys.stdout.write('\n')
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
    args = parse_arguments()

    hosts = os.path.join(os.getcwd(), 'hosts')
    become = ' --ask-become' if (not args.disable_become) else ''
    os.chdir(PLAYBOOK_PATH)
    run('ansible-playbook -i %s -l %s site.yml%s'%(hosts, args.deploy, become))
