"""Console script for keystonescan."""

import sys
import argparse
from keystonescan import keystonescan

def main():
    """Console script for keystonescan."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", default=".", metavar="DIR", dest="input_dir",
            help="location of input data files (e.g. 'toons.json' and 'access.json')")
    parser.add_argument("-o", "--output", default=".", metavar="DIR", dest="output_dir",
            help="location to write output files")
    parser.add_argument("-p", "--player", action="store_true", help="output player data")
    parser.add_argument("-c", "--character", action="store_true", help="output character data")
    parser.add_argument("-d", "--dungeon", action="store_true", help="output dungeon data")
    args = parser.parse_args()

    return keystonescan.scan(**vars(args))

if __name__ == "__main__":
    sys.exit(main())
