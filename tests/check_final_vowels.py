from get_vowels_multi import get_vowels_multi

text = 'ญัตติที่เสนอได้ผ่านที่ประชุมด้วยมติเอกฉันท์'
vowel_groups = get_vowels_multi(text)

print(f'Found {len(vowel_groups)} vowel groups:')
vowel_marks = {'า', 'ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู', 'เ', 'แ', 'โ', 'ใ', 'ไ', 'ั', 'ำ', 'ะ', '็'}

for vowel_num in sorted(vowel_groups.keys()):
    interpretations = vowel_groups[vowel_num]

    # Find vowel marks in this group
    vowel_marks_found = set()
    min_pos = min(interp['start_pos'] for interp in interpretations)
    max_pos = max(interp['end_pos'] for interp in interpretations)

    for interp in interpretations:
        for char in interp['matched_text']:
            if char in vowel_marks:
                vowel_marks_found.add(char)

    print(f'Vowel {vowel_num}: {vowel_marks_found} at positions {min_pos}-{max_pos}')

    # Show one example
    example = interpretations[0]
    print(f'  Example: {example["pattern"]} - "{example["matched_text"]}"')
    print()