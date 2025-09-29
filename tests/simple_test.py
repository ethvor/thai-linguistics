from get_vowels_multi import get_vowels_multi

text = 'ญัตติที่เสนอได้ผ่านที่ประชุมด้วยมติเอกฉันท์'
vowel_groups = get_vowels_multi(text)

print('Total:', len(vowel_groups))

# Check the last few vowels specifically
for num in [14, 15, 16, 17, 18]:
    if num in vowel_groups:
        interps = vowel_groups[num]
        print(f'Vowel {num}: {len(interps)} interpretations')
        for interp in interps:
            print(f'  {interp["pattern"]} - {interp["matched_text"]} Pos: {interp["start_pos"]}-{interp["end_pos"]}')