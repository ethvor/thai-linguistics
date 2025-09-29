from get_vowels_multi import get_vowels_multi

text = 'ญัตติที่เสนอได้ผ่านที่ประชุมด้วยมติเอกฉันท์'
vowel_groups = get_vowels_multi(text)

print('Analysis of vowel grouping:')
for vowel_num in sorted(vowel_groups.keys()):
    interpretations = vowel_groups[vowel_num]
    print(f'\nVowel {vowel_num}: ({len(interpretations)} interpretations)')

    for i, interp in enumerate(interpretations):
        print(f'  [{i+1}] Pattern: {interp["pattern"]} Text: "{interp["matched_text"]}" Pos: {interp["start_pos"]}-{interp["end_pos"]}')

    # Show the character span this vowel group covers
    min_pos = min(interp["start_pos"] for interp in interpretations)
    max_pos = max(interp["end_pos"] for interp in interpretations)
    span_text = text[min_pos:max_pos+1]
    print(f'    Covers: pos {min_pos}-{max_pos} = "{span_text}"')