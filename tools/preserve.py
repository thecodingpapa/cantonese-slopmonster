#!/usr/bin/env python3
"""Compare literal anchors between drafts. No semantic or factual guarantee."""
import argparse
from collections import Counter
import json
import re
import sys

from text_regions import read_utf8, regions

NUMBER = re.compile(r'[0-9０-９]+(?:[.,，．:/：-][0-9０-９]+)*(?:[%％])?')
URL = re.compile(r'https?://[^\s<>\]\)」』”。，；！？]+')


def anchors(text, locks=()):
    result = Counter()
    for m in NUMBER.finditer(text):
        result[('number', m[0])] += 1
    for m in URL.finditer(text):
        result[('url', m[0])] += 1
    spans, warnings = regions(text)
    for r in spans:
        if r.kind in {'quote', 'code', 'cue', 'link_target'}:
            result[(r.kind, text[r.start:r.end])] += 1
    for value in dict.fromkeys(locks):
        result[('lock', value)] = text.count(value)
    return result, warnings


def compare(before, after, locks=()):
    old, old_warnings = anchors(before, locks)
    new, new_warnings = anchors(after, locks)
    def changes(diff):
        return [{'kind': k, 'text': v, 'count': count} for (k, v), count in sorted(diff.items())]
    missing_locks = [v for v in dict.fromkeys(locks) if not v or v not in before]
    removed, added = changes(old - new), changes(new - old)
    valid = bool(before.strip()) and bool(after.strip()) and not missing_locks
    return {'status': 'invalid_input' if not valid else 'changed' if removed or added or old_warnings or new_warnings else 'anchors_unchanged',
            'removed': removed, 'added': added, 'locks_not_in_original': missing_locks,
            'warnings': old_warnings + new_warnings, 'meaning_verified': False,
            'note': '只比較字面標記同出現次數；未核對事實、單位、否定、因果、歸屬或整體意思。'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before')
    parser.add_argument('after')
    parser.add_argument('--lock', action='append', default=[], help='必須逐字保留嘅名稱／數字連單位／限制條件；可重複使用')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    try:
        report = compare(read_utf8(args.before), read_utf8(args.after), args.lock)
    except (OSError, UnicodeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False) if args.json else str(exc), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(report['status'])
        for label in ('removed', 'added'):
            for item in report[label]:
                print(f"{label}: {item['kind']} ×{item['count']} — {item['text']}")
        for value in report['locks_not_in_original']:
            print('原稿搵唔到 lock：' + value)
        for warning in report['warnings']:
            print(warning)
        print(report['note'])
    return 2 if report['status'] == 'invalid_input' else 0 if report['status'] == 'anchors_unchanged' else 1


if __name__ == '__main__':
    sys.exit(main())
