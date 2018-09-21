# !usr/bin/env python

from __future__ import print_function, division, absolute_import
import click
import invoke
import os
import sys


CURDIR = os.path.abspath(os.curdir)

def write_header(name=None, version='master'):
    ''' Write proper file header in a given shell format

    Parameters:
        name (str):
            The name of the product
        version (str):
            version name of the module file

    Returns:
        A string header to insert
    '''


    product_dir = os.path.join(CURDIR, name)

    hdr = """#%Module1.0
proc ModulesHelp {{ }} {{
    global product version
    puts stderr "This module adds $product/$version to various paths"
}}
set name {1}
set product {1}
set version {2}
conflict $product
module-whatis "Sets up $product/$version in your environment"

set PRODUCT_DIR {0}
setenv [string toupper $product]_DIR $PRODUCT_DIR
setenv [string toupper $product]_VER $version
prepend-path PATH $PRODUCT_DIR/bin
prepend-path PYTHONPATH $PRODUCT_DIR/python

                """.format(product_dir, name, version)

    return hdr.strip()

def get_pythonpath(name):
    ''' get a python path '''
    path = os.path.join(CURDIR, name)
    bindir = os.path.join(path, 'bin')
    pythondir = os.path.join(path, 'python')
    namedir = os.path.join(path, name)
    pypath = pythondir if os.path.isdir(pythondir) else namedir if os.path.isdir(namedir) else None
    return pypath


def get_modules_dir(modules_path):
    # find or define a modules path
    if not modules_path:
        modulepath = os.getenv("MODULEPATH")
        if not modulepath:
            modules_path = input('Enter the root path for your module files:')
        else:
            split_mods = modulepath.split(':')
            modules_path = split_mods[0]

    return modules_path


@click.command()
@click.option('-n', '--name', help='Name of program to install', required=True)
@click.option('-m', '--method', type=click.Choice(['modules', 'setup', 'env', 'pip']), help='Method of installation')
@click.option('-d', '--modulesdir', envvar='MODULES_DIR', help='path to your module files')
@click.option('-b', '--branch', default='master', help='module file version to use')
def quickinstall(name, method, modulesdir, branch):
    ''' Method to quickly install a product '''

    if method == 'modules':
        version = 'master'
        module = write_header(name, version=branch)
        modulesdir = get_modules_dir(modulesdir)

        submod = os.path.join(modulesdir, name)
        if not os.path.isdir(submod):
            os.makedirs(submod)

        filename = os.path.join(submod, branch)            
        with open(filename, 'w') as f:
            f.write(module)
        return
    elif method == 'setup':
        os.chdir(name)
        cmd = 'python setup.py install'
    elif method == 'env':
        isdir = os.path.isdir(name)            
        pypath = get_pythonpath(name)

        exp = 'export {0}_DIR={1}; export PATH=$PATH:{2}; export PYTHONPATH=$PYTHONPATH:{3}'.format(name.upper(), path, bindir, pypath)
        bashrc = os.path.join(os.path.expanduser('~'), '.bashrc')
        cmd = "echo -e '\n # {0} setup \n {1}' >> {2}".format(name, exp, bashrc)
    elif method == 'pip':
        cmd = 'pip install {0}'.format(name)
    else:
        print('No method found.  Cannot install program {0}'.format(name))
        return

    res = invoke.run(cmd, hide='both', warn=True)
    if not res.ok:
        print('Failed to install via {0}:'.format(method), res.stdout)    

if __name__ == "__main__":
    quickinstall()

