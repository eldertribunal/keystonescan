"""Console script for keystonescan."""

import sys
import argparse
from keystonescan import keystonescan

def main():
    """Console script for keystonescan."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", default=".", metavar="DIR",
            help="location of input data files (e.g. 'toons.json' and 'access.json')")
    parser.add_argument("-o", "--output", default=".", metavar="DIR",
            help="location to write output files")
    args = parser.parse_args()

    return keystonescan.scan(args.input, args.output)

if __name__ == "__main__":
    sys.exit(main())
