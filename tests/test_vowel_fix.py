#!/usr/bin/env python3
import sys
import io

# Set UTF-8 encoding for Windows console (skip in Jupyter)
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from get_vowels_multi import get_vowels_multi

text = 'ญัตติที่เสนอได้ผ่านที่ประชุมด้วยมติเอกฉันท์'
vowel_groups = get_vowels_multi(text)

print(f'Total vowel groups found: {len(vowel_groups)}')
print()

# Show the last few vowels to see if 17/18 are now merged
for vowel_num in sorted(vowel_groups.keys())[-5:]:
    interpretations = vowel_groups[vowel_num]
    print(f'Vowel {vowel_num}: ({len(interpretations)} interpretations)')
    for i, interp in enumerate(interpretations, 1):
        print(f'  [{i}] {interp["pattern"]} - "{interp["matched_text"]}" Pos: {interp["start_pos"]}-{interp["end_pos"]}')
    print()