import argparse
import os
import sys
from .transpiler import transpile_file, compile_c

def main():
    parser = argparse.ArgumentParser(prog="cpile")
    subparsers = parser.add_subparsers(dest="command")
    transpile = subparsers.add_parser("transpile", help ="transpile .py file")
    transpile.add_argument("file", help="input python .py file")
    transpile.add_argument("-o", "--output", help="transpile output file path (Optional)")

    build = subparsers.add_parser("build", help="build output executable file")
    build.add_argument("file", help="input file to build")
    build.add_argument("-o", "--output", help="build output file path for executable file")

    args=parser.parse_args()

    if args.command == "transpile":
        if os.path.exists(args.file):
            c_code = transpile_file(args.file)
            if args.output:
                with open(args.output, "w") as f:
                    f.write(c_code)
            else: 
                print(c_code)

        else:
            raise FileNotFoundError(f"Input file not found '{args.file}'")
    if args.command == "build":
        if os.path.exists(args.file):
            c_code = transpile_file(args.file)
            if args.output:
                compile_c(c_code, output_name=args.output)
            else:
                compile_c(c_code)
        else :
            raise FileNotFoundError(f"Input file not found '{args.file}'")

if __name__ == "__main__":
    main()