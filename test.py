import sys


import nose

import re
import glob
import subprocess

def run_python_tests():
    loader = nose.loader.TestLoader(workingDir='python')
    python_success = nose.run(testLoader=loader)

    if (python_success):
        print 'All python tests passed'
    else:
        print 'Python tests failed'

    return python_success

def run_vspec_tests():
    vim_success = False

    total_passed = 0
    total_run = 0

    for name in glob.glob('tests/**.vim'):
        cmd = ['./deps/vim-vspec/bin/vspec',
               './deps/vim-vspec', '.',
               name]

        try:
            output = subprocess.check_output(cmd)
        except Exception as e:
            print e
            raise


        passed, run = get_vspec_pass_fail(output)
        output = format_vspec_output(output)
        print output

        if run != '?':
            total_passed += int(passed)
            total_run += int(run)

    print

    if total_passed == total_run:
        vim_success = True
        print 'All {0} vspec tests passed'.format(total_passed)
    else:
        failed = total_run - total_passed
        print '{0} of {1} vspec tests failed'.format(failed, total_run)

    return vim_success


def format_vspec_output(output):
    output_lines = output.split('\n')
    formatted_lines = []

    for line in output_lines[:-2]:
        f_line = line

        if line.startswith("ok"):
            f_line = f_line

        if line.startswith("not ok"):
            f_line = f_line

        if line.startswith("#"):
            f_line = "    " + line[1:]

        formatted_lines.append(f_line)

    return '\n'.join(formatted_lines)

def get_vspec_pass_fail(output):
    output_lines = output.split('\n')
    passed = len(filter(lambda x: x.startswith("ok "), output_lines))
    total = len(filter(lambda x: x.startswith("ok ") \
            or x.startswith("not ok ") \
            or "SEGV" in x, output_lines))

    return passed, total

if __name__ == '__main__':
    print "Running python tests:"
    print
    python_success = run_python_tests()

    print
    print "Running vspec tests:"
    print 
    vspec_success = run_vspec_tests()

    print "-------------------------------"

    if (not python_success and not vspec_success):
        sys.exit("Python and vspec tests failed")

    if (not python_success):
        sys.exit("Python tests failed")

    if (not vspec_success):
        sys.exit("vspec tests failed")

    sys.exit()
