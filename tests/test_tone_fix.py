from get_vowels_multi import get_vowels_multi, strip_tone_marks

text = 'ญัตติที่เสนอได้ผ่านที่ประชุมด้วยมติเอกฉันท์'

print('Testing tone mark stripping:')
stripped, tone_positions = strip_tone_marks(text)
print(f'Original:  "{text}"')
print(f'Stripped:  "{stripped}"')
print(f'Tone positions: {tone_positions}')

print('\nTesting vowel finding with tone mark ignoring:')
vowel_groups = get_vowels_multi(text)
print(f'Total vowel groups found: {len(vowel_groups)}')

# Check specifically for า vowel patterns
print('\nLooking for า vowel patterns:')
for vowel_num, interpretations in vowel_groups.items():
    for interp in interpretations:
        if 'า' in interp['matched_text']:
            print(f'Vowel {vowel_num}: {interp["pattern"]} - "{interp["matched_text"]}" Pos: {interp["start_pos"]}-{interp["end_pos"]}')