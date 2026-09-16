#!/usr/bin/env python3
"""Read-only, offline heuristics for Traditional written conversational Cantonese."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

from text_regions import is_han, narration, read_utf8

VERSION = '0.1.0'
RULES = json.loads(Path(__file__).with_name('rules.json').read_text(encoding='utf-8'))
CANTO = re.compile(r'我哋|你哋|佢哋|佢|唔|冇|嘅|咗|喺|嚟|嗰|呢個|呢啲|點樣|點解|乜|咩|畀|俾|啱|睇|搵|嘢|噉|咁|啲|㗎|𠵱|鍾意|好多')
OTHER_SCRIPT = re.compile(r'[\u3040-\u30ff\uac00-\ud7af]')


def audit(text, markdown=True, include_quotes=False):
    body, spans, warnings = narration(text, markdown, include_quotes)
    han = sum(is_han(c) for c in body)
    cues = len(CANTO.findall(body))
    eligible = sum(c.isalnum() for c in body)
    status = ('empty' if not eligible else 'unsupported' if not han else
              'insufficient' if han < 8 else 'mixed_language' if OTHER_SCRIPT.search(body)
              else 'review_language' if not cues else 'checked')
    if warnings and status == 'checked':
        status = 'review_markup'
    reasons = {
        'empty': '冇可檢查嘅旁白；可能係空白或全部屬引文／程式碼／拍攝提示。',
        'unsupported': '冇足夠漢字旁白；本工具唔支援純英文等其他語言。',
        'insufficient': '少於 8 個漢字，只能提供局部提示，唔足以判斷語體。',
        'mixed_language': '包含日文假名或韓文；只能局部檢查，請人手確認語言。',
        'review_language': '未見有限字表內嘅廣東話標記；可能係共通中文，請人手確認，唔好為過關硬加字。',
        'review_markup': '標記未配對，檢查範圍可能唔完整。',
        'checked': '已對可辨識旁白套用有限規則；未命中唔代表自然、準確或完整。',
    }
    hits = []

    def add(rule_id, category, start, end, title, advice):
        hits.append({'id': rule_id, 'category': category, 'line': text.count('\n', 0, start) + 1,
                     'column': start - text.rfind('\n', 0, start), 'start': start, 'end': end,
                     'excerpt': text[start:end], 'title': title, 'advice': advice})

    for rule in RULES:
        for m in re.finditer(rule['pattern'], body):
            add(rule['id'], rule['category'], m.start(), m.end(), rule['title'], rule['advice'])
    seen = set()
    for m in re.finditer(r'[^。！？!?\n\0]+', body):
        fragment = m[0].strip()
        if not fragment:
            continue
        start = m.start() + len(m[0]) - len(m[0].lstrip())
        key = ''.join(c for c in fragment if c.isalnum())
        count = sum(is_han(c) for c in fragment)
        if count >= 8 and key in seen:
            add('W203', 'writing', start, m.end(), '有一句重複咗',
                '確認係咪刻意重申、對話或副歌；冇作用先刪，重要限制條件唔好刪。')
        seen.add(key)
        if count > 90:
            add('W204', 'writing', start, m.end(), '口述句子較長',
                '超過 90 個漢字未有句末停頓；按意思分句，保留因果、否定同限制條件。')
    hits.sort(key=lambda h: (h['start'], h['id']))
    return {'version': VERSION, 'status': 'no_findings' if status == 'checked' and not hits else 'needs_review',
            'coverage': {'status': status, 'reason': reasons[status], 'han_characters': han,
                         'cantonese_markers': cues, 'eligible_letters_and_digits': eligible,
                         'excluded_characters': sum(r.end - r.start for r in spans),
                         'excluded_regions': dict(Counter(r.kind for r in spans)), 'warnings': warnings},
            'summary': {'register': sum(h['category'] == 'register' for h in hits),
                        'writing': sum(h['category'] == 'writing' for h in hits)},
            'findings': hits, 'meaning_verified': False,
            'note': '人手編寫嘅啟發式規則；唔係 AI 偵測器，亦冇品質滿分。'}


def exit_code(report):
    return 2 if report['coverage']['status'] == 'empty' else 0 if report['status'] == 'no_findings' else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('file', nargs='?', help='UTF-8 .md/.txt，或 - 讀 stdin')
    group.add_argument('--text', help='直接輸入文字')
    parser.add_argument('--format', choices=['markdown', 'plain'], default='markdown')
    parser.add_argument('--include-quotes', action='store_true', help='連引文都檢查；預設略過')
    parser.add_argument('--json', action='store_true', help='輸出 JSON')
    args = parser.parse_args(argv)
    try:
        text = args.text if args.text is not None else sys.stdin.read() if args.file == '-' else read_utf8(args.file)
        report = audit(text, args.format == 'markdown', args.include_quotes)
    except (OSError, UnicodeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False) if args.json else f'讀取失敗：{exc}', file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Cantonese SlopMonster {VERSION} — {report['status']}")
        print(f"範圍：{report['coverage']['status']} — {report['coverage']['reason']}")
        print(f"語體提示 {report['summary']['register']}；表達提示 {report['summary']['writing']}")
        print('略過區域：' + json.dumps(report['coverage']['excluded_regions'], ensure_ascii=False))
        for warning in report['coverage']['warnings']:
            print('標記提示：' + warning)
        for h in report['findings']:
            print(f"L{h['line']}:{h['column']} {h['id']} {h['title']} — {h['excerpt']}")
            print('  ' + h['advice'])
        print(report['note'])
    return exit_code(report)


if __name__ == '__main__':
    sys.exit(main())
