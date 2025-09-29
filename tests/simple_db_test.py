import sys, io
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from get_vowels_multi import get_vowels_multi

text = 'ผ่าน'  # Simple test with tone mark
vowel_groups = get_vowels_multi(text)

print('Testing tone mark preservation:')
for vowel_num, interpretations in vowel_groups.items():
    for interp in interpretations:
        syllable_text = interp['matched_text']
        print(f'Syllable: "{syllable_text}"')
        if 'า' in syllable_text:
            if '่' in syllable_text:
                print('  ✓ Tone mark preserved')
            else:
                print('  ✗ Tone mark missing')
        print(f'  Pattern: {interp["pattern"]}')
        print()