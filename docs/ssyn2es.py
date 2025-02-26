#!/usr/bin/env python

import argparse
import fileinput


def parse_args():
    parser = argparse.ArgumentParser(
        prog="ssyn2es.py", description="convert Sudachi synonyms to Solr format")
    parser.add_argument('files', metavar='FILE', nargs='*',
                        help='files to read, if empty, stdin is used')

    parser.add_argument('-p', '--output-predicate', action='store_true',
                        help='if set, output predicates')
    args = parser.parse_args()
    return args


def load_synonyms(files, output_predicate):
    synonyms = {}
    with fileinput.input(files=files) as input:
        for line in input:
            line = line.strip()
            if line == "":
                continue
            entry = line.split(",")[0:9]
            if entry[2] == "2" or (not output_predicate and entry[1] == "2"):
                continue
            group = synonyms.setdefault(entry[0], [[], []])
            group[1 if entry[2] == "1" else 0].append(entry[8])

    return synonyms


def dump_synonyms(synonyms, file=None):
    for groupid in sorted(synonyms):
        group = synonyms[groupid]
        if not group[1]:
            if len(group[0]) > 1:
                print(",".join(group[0]), file=file)
        else:
            if len(group[0]) > 0 and len(group[1]) > 0:
                print(",".join(group[0]) + "=>" +
                      ",".join(group[0] + group[1]), file=file)
    return


def main():
    args = parse_args()

    synonyms = load_synonyms(args.files, args.output_predicate)
    dump_synonyms(synonyms)


if __name__ == "__main__":
    main()
