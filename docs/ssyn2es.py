#!/usr/bin/env python

import argparse
import fileinput
import re
import sys
import unicodedata


def parse_args():
    parser = argparse.ArgumentParser(
        prog="ssyn2es.py", description="convert Sudachi synonyms to Solr format")
    parser.add_argument('files', metavar='FILE', nargs='*',
                        help='files to read, if empty, stdin is used')

    parser.add_argument("--discard-punctuation", action='store_true',
                        help='if set, skip words that consist of puctuation chars')
    parser.add_argument('-p', '--output-predicate', action='store_true',
                        help='if set, output predicates')
    args = parser.parse_args()
    return args


def load_synonyms(files, output_predicate, discard_punctuation):
    synonyms = {}
    with fileinput.input(files=files) as input:
        for i, line in enumerate(input):
            line = line.strip()
            if line == "":
                continue

            entry = line.split(",")[0:9]
            headword = escape_comma(unescape_unicode_literal(entry[8]))

            is_deleted = (entry[2] == "2")
            is_predicate = (entry[1] == "2")
            if is_deleted or (is_predicate and not output_predicate):
                continue
            if (is_punctuation_word(headword) and discard_punctuation):
                print(f"skip punctuation entry {entry[8]} at line {i}",
                      file=sys.stderr)
                continue

            group = synonyms.setdefault(entry[0], [[], []])
            group[1 if entry[2] == "1" else 0].append(headword)

    return synonyms


unicode_literal_pattern = re.compile(
    r"""\\u([0-9a-fA-F]{4}|\{[0-9a-fA-F]+\})""")


def _repl_uncode_literal(m):
    return chr(int(m.group(1).strip("{}"), 16))


def unescape_unicode_literal(word):
    return unicode_literal_pattern.sub(_repl_uncode_literal, word)


def escape_comma(word):
    return word.replace(",", "\,")


# Unicode General Category list, that is used for punctuation in elasticsearch_sudachi
# see: com.worksap.nlp.lucene.sudachi.ja.util.Strings
punctuation_categories = [
    "Zs",  # Character.SPACE_SEPARATOR
    "Zl",  # Character.LINE_SEPARATOR
    "Zp",  # Character.PARAGRAPH_SEPARATOR
    "Cc",  # Character.CONTROL
    "Cf",  # Character.FORMAT
    "Pd",  # Character.DASH_PUNCTUATION
    "Ps",  # Character.START_PUNCTUATION
    "Pe",  # Character.END_PUNCTUATION
    "Pc",  # Character.CONNECTOR_PUNCTUATION
    "Po",  # Character.OTHER_PUNCTUATION
    "Sm",  # Character.MATH_SYMBOL
    "Sc",  # Character.CURRENCY_SYMBOL
    "Sk",  # Character.MODIFIER_SYMBOL
    "So",  # Character.OTHER_SYMBOL
    "Pi",  # Character.INITIAL_QUOTE_PUNCTUATION
    "Pf",  # Character.FINAL_QUOTE_PUNCTUATION
]


def is_punctuation_word(word: str):
    # return True if all characters are in punctuation categories.
    for c in word:
        category = unicodedata.category(c)
        if category not in punctuation_categories:
            return False
    return True


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

    synonyms = load_synonyms(
        args.files,
        args.output_predicate,
        args.discard_punctuation,
    )
    dump_synonyms(synonyms)


if __name__ == "__main__":
    main()
