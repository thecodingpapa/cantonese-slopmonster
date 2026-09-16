import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from check import audit, exit_code
from preserve import compare
from text_regions import is_han, narration


class CantoneseBehavior(unittest.TestCase):
    def test_natural_script_and_shared_words(self):
        result = audit('我哋需要兩個轉插，因為插頭唔啱。如果你已經有，就唔使再買。')
        self.assertEqual(result['status'], 'no_findings')
        self.assertFalse(result['meaning_verified'])

    def test_awkward_draft_has_both_kinds_of_feedback(self):
        result = audit('我們將展示這個工具，帶來無縫體驗，重新定義工作方式。')
        self.assertGreater(result['summary']['register'], 0)
        self.assertGreater(result['summary']['writing'], 0)
        self.assertEqual(result['coverage']['status'], 'review_language')
        self.assertEqual(exit_code(result), 1)

    def test_shared_words_are_not_blanket_banned(self):
        self.assertEqual(audit('如果需要，我哋可以用呢個方法，因為結果比較清楚。')['findings'], [])

    def test_english_technical_terms(self):
        self.assertEqual(audit('呢個 app 會用 API 傳資料，timeout 就設做 30 秒。')['status'], 'no_findings')

    def test_variant_cantonese_characters(self):
        self.assertTrue(is_han('𠵱'))
        result = audit('𠵱家畀啲時間佢，噉樣做都得㗎。')
        self.assertEqual(result['status'], 'no_findings')

    def test_simplified_mixed_draft(self):
        result = audit('我哋而家睇下这些说明，呢度讲嘅係設定。')
        self.assertIn('R105', [h['id'] for h in result['findings']])

    def test_quotes_are_preserved_and_excluded(self):
        result = audit('佢話「我們沒有收到通知」。我哋睇返文件先。')
        self.assertEqual(result['findings'], [])
        self.assertEqual(result['coverage']['excluded_regions']['quote'], 1)

    def test_nested_quotes_and_smart_quotes(self):
        result = audit('佢話「文件寫『我們沒有資料』」；我哋再睇 “這個設定”。')
        self.assertEqual(result['findings'], [])

    def test_quotes_with_inline_code(self):
        result = audit('佢話「我們要用 `API`，沒有其他要求」。我哋再睇清楚先。')
        self.assertEqual(result['findings'], [])

    def test_include_quotes_for_authored_dialogue(self):
        text = '佢話「我們沒有收到通知」。我哋睇返文件先。'
        self.assertGreater(len(audit(text, include_quotes=True)['findings']), 0)

    def test_production_cues_timestamps_and_code(self):
        text = '''[00:10]
[畫面：我們的示範]
【字幕：這個方法】
```python
print("我們沒有資料")
```
我哋而家睇下呢個方法，試完先再講。'''
        result = audit(text)
        self.assertEqual(result['findings'], [])
        self.assertGreater(result['coverage']['excluded_characters'], 0)

    def test_tilde_fence_and_long_fence(self):
        for fence in ('~~~', '````'):
            result = audit(f'{fence}\n我們沒有資料\n{fence}\n我哋睇下呢個設定先，唔使急。')
            self.assertEqual(result['findings'], [])

    def test_headings_blockquotes_and_inline_code(self):
        text = '# 我們的設定\n> 這個沒有用\n我哋睇下 `我們` 呢個字點用先。'
        self.assertEqual(audit(text)['findings'], [])
        self.assertGreater(len(audit(text, markdown=False)['findings']), 0)

    def test_link_label_is_checked_but_target_is_not(self):
        result = audit('我哋睇 [這個設定](https://example.com/我們)，再慢慢試。')
        self.assertEqual([h['excerpt'] for h in result['findings']], ['這個'])

    def test_bracketed_speech_is_not_hidden(self):
        result = audit('我哋再講一次：[這個沒有用]，但要睇情況。')
        self.assertGreater(len(result['findings']), 0)

    def test_position_survives_excluded_regions(self):
        text = '[畫面：我們]\n我哋先睇。這個要留意。'
        finding = audit(text)['findings'][0]
        self.assertEqual((finding['line'], finding['column']), (2, 6))
        self.assertEqual(text[finding['start']:finding['end']], '這個')

    def test_no_matching_across_excluded_regions(self):
        text = '我`code`們睇下呢個設定，應該可以用。'
        self.assertNotIn('R101', [h['id'] for h in audit(text)['findings']])

    def test_repetition_feedback(self):
        result = audit('我哋今日試下呢個方法。\n我哋今日試下呢個方法。')
        self.assertIn('W203', [h['id'] for h in result['findings']])

    def test_long_spoken_run(self):
        result = audit('我哋' + '測試內容' * 24 + '。')
        self.assertIn('W204', [h['id'] for h in result['findings']])

    def test_short_empty_foreign_and_common_chinese_are_not_passes(self):
        for text, coverage in [('', 'empty'), ('   ！！', 'empty'), ('我唔知。', 'insufficient'),
                               ('This is a clear English script.', 'unsupported'),
                               ('今天的天氣晴朗，適合散步。', 'review_language'),
                               ('我哋今日見到呢個例子です。', 'mixed_language')]:
            with self.subTest(text=text):
                result = audit(text)
                self.assertEqual(result['coverage']['status'], coverage)
                self.assertNotEqual(exit_code(result), 0)

    def test_all_excluded_is_not_clean(self):
        for text in ('「我們沒有資料」', '```\n我哋睇下呢個設定\n```', '[畫面：我哋睇下呢個設定]'):
            self.assertEqual(exit_code(audit(text)), 2)

    def test_unclosed_markup_is_reported(self):
        for text in ('我哋睇下呢個設定先。\n```\n我們沒有資料', '我哋睇下呢個設定「未完'):
            result = audit(text)
            self.assertTrue(result['coverage']['warnings'])
            self.assertNotEqual(exit_code(result), 0)

    def test_bundled_before_and_after(self):
        before = (ROOT / 'examples/before.md').read_text(encoding='utf-8')
        after = (ROOT / 'examples/after.md').read_text(encoding='utf-8')
        self.assertEqual(exit_code(audit(before)), 1)
        self.assertEqual(exit_code(audit(after)), 0)
        self.assertEqual(compare(before, after, ['Rain is here', '10 分鐘'])['status'], 'anchors_unchanged')


class PreservationBehavior(unittest.TestCase):
    def test_changed_data_quotes_and_cues(self):
        before = '[00:10]\n[畫面：手機]\nRain is here：等 30 秒。佢話「未必有效」。https://example.com/a'
        after = '[00:20]\n[畫面：電腦]\nRain is here：等 60 秒。佢話「一定有效」。https://example.com/b'
        report = compare(before, after)
        self.assertEqual(report['status'], 'changed')
        kinds = {x['kind'] for x in report['removed']}
        self.assertTrue({'number', 'url', 'cue', 'quote'} <= kinds)

    def test_exact_names_units_and_caveats_can_be_locked(self):
        before = 'Rain is here：等 30 秒，只限示範。'
        for after in ('Rain is here：等 30 分鐘，只限示範。', 'Rain is here：等 30 秒。', 'Rain is there：等 30 秒，只限示範。'):
            self.assertEqual(compare(before, after, ['Rain is here', '30 秒', '只限示範'])['status'], 'changed')

    def test_invalid_lock_not_silently_ignored(self):
        self.assertEqual(compare('我哋試下。', '我哋試下。', ['Rain is here'])['status'], 'invalid_input')

    def test_repeated_numbers_count_and_fullwidth(self):
        report = compare('10 分鐘，再等 10 分鐘，最後 ３０ 秒。', '10 分鐘，最後 30 秒。')
        self.assertEqual(report['status'], 'changed')
        self.assertTrue(any(x['text'] == '３０' for x in report['removed']))

    def test_code_change_is_visible(self):
        self.assertEqual(compare('執行 `wait(30)`。', '執行 `sleep(30)`。')['status'], 'changed')

    def test_semantic_limit_is_explicit(self):
        report = compare('A 用 10 秒，B 用 20 秒。', 'A 用 20 秒，B 用 10 秒。')
        self.assertEqual(report['status'], 'anchors_unchanged')
        self.assertFalse(report['meaning_verified'])

    def test_empty_draft_is_invalid(self):
        self.assertEqual(compare('', '')['status'], 'invalid_input')
        self.assertEqual(compare('我哋睇下。', '')['status'], 'invalid_input')


class CommandLineBehavior(unittest.TestCase):
    def run_tool(self, tool, *args, **kwargs):
        return subprocess.run([sys.executable, str(ROOT / 'tools' / tool), *args],
                              capture_output=True, text=True, **kwargs)

    def test_text_stdin_and_file_agree(self):
        text = '我哋今日睇下呢個設定，唔使急。'
        results = [self.run_tool('check.py', '--text', text, '--json'),
                   self.run_tool('check.py', '-', '--json', input=text)]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / '粵語 稿.md'
            path.write_text('\ufeff' + text, encoding='utf-8')
            results.append(self.run_tool('check.py', str(path), '--json'))
        for result in results:
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len({r.stdout for r in results}), 1)

    def test_invalid_utf8_and_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'bad.txt'
            path.write_bytes(b'\xff\xfe')
            for file in (str(path), str(Path(tmp) / 'absent.txt')):
                result = self.run_tool('check.py', file, '--json')
                self.assertEqual(result.returncode, 2)
                self.assertIn('error', json.loads(result.stderr))

    def test_check_never_modifies_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'draft.md'
            original = '我們會展示這個設定。'.encode('utf-8')
            path.write_bytes(original)
            self.run_tool('check.py', str(path))
            self.assertEqual(path.read_bytes(), original)

    def test_json_matches_exit_status(self):
        for text, code in [('', 2), ('English only.', 1), ('我們沒有資料。', 1)]:
            result = self.run_tool('check.py', '--text', text, '--json')
            self.assertEqual(result.returncode, code)
            self.assertEqual(json.loads(result.stdout)['status'], 'needs_review')

    def test_preserve_cli(self):
        result = self.run_tool('preserve.py', str(ROOT / 'examples/before.md'),
                               str(ROOT / 'examples/after.md'), '--lock', 'Rain is here', '--json')
        self.assertEqual(result.returncode, 0)
        self.assertFalse(json.loads(result.stdout)['meaning_verified'])


if __name__ == '__main__':
    unittest.main()
