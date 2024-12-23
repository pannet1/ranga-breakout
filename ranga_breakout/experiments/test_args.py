# program to check print argument passed while initializing the script
# for example python test_args.py "hello world"
#
import sys

args = sys.argv[1:]
if len(args) > 0:
    print(type(args))
