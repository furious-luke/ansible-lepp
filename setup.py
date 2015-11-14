#!/usr/bin/env python

import os, sys, subprocess, argparse

__all__ = ['Ansible']


class Ansible(object):

    def __init__(self, run_path=None):
        self.run_path = run_path

    def __call__(self):
        self.check_ansible_version()
        self.check_ansible_python()
        parser = self.setup_arguments()
        args = self.parse_arguments(parser)
        cmd = self.prepare_command(args)
        self.run_ansible(cmd, args)

    def run(self, cmd, output=False):
        if output:
            return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        else:
            subprocess.check_call(cmd, shell=True)

    def check_ansible_version(self):
        try:
            output = self.run('ansible-playbook --version', True)
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

    def check_ansible_python(self):
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

    def setup_arguments(self):
        parser = argparse.ArgumentParser('Setup Django Python environment.')
        parser.add_argument('--project', '-p', help='project name')
        parser.add_argument('--deploy', '-d', choices=['development', 'production'], default='development',
                            help='deployment type')
        parser.add_argument('--installation', '-i', help='installation name (defaults to project name)')
        parser.add_argument('--branch', '-b', help='repository branch')
        parser.add_argument('--no-clone', '-c', action='store_true', help='do not clone the repository')
        parser.add_argument('--disable-become', action='store_true', help='disable promotion')
        parser.add_argument('--dry-run', action='store_true', help='show Ansible command only')
        return parser


    def parse_arguments(self, parser):
        args = parser.parse_args()
        args.deploy = args.deploy.lower()
        return args


    def prepare_command(self, args):
        hosts = os.path.join(os.getcwd(), 'hosts')
        become = ' --ask-become' if (not args.disable_become) else ''
        proj_name = ('project=%s'%args.project) if args.project else None
        inst_name = ('inst_name=%s'%(args.installation if args.installation else args.project) if args.project else None)
        branch = ('repository_branch=%s'%args.branch) if args.branch else None
        clone = 'clone_repository=False' if args.no_clone else None

        extra_args = become
        extra_vars = filter(lambda x: x is not None, [proj_name, branch, clone, inst_name])
        if extra_vars:
            extra_vars = ' --extra-vars "%s"'%' '.join(extra_vars)
            extra_args += extra_vars
        return (hosts, args.deploy, extra_args)

    def run_ansible(self, cmd, args):
        if self.run_path:
            os.chdir(self.run_path)
        cmd = 'ansible-playbook -i %s -l %s site.yml%s'%cmd
        if args.dry_run:
            sys.stdout.write(cmd + '\n')
        else:
            self.run(cmd)


if __name__ == '__main__':
    Ansible()()
