from get_vowels_multi import get_vowels_multi
from thai_syllable_database import syllable_query, PatternData

text = 'ญัตติที่เสนอได้ผ่านที่ประชุมด้วยมติเอกฉันท์'
vowel_groups = get_vowels_multi(text)

print('Testing database storage with tone marks preserved:')

# Focus on vowel 6 which contains the า with tone marks
vowel_6_interpretations = vowel_groups[6]

print(f'\nVowel 6 has {len(vowel_6_interpretations)} interpretations:')

for i, interp in enumerate(vowel_6_interpretations, 1):
    print(f'[{i}] Pattern: {interp["pattern"]} - Text: "{interp["matched_text"]}"')
    print(f'    x="{interp.get("x_text", "")}" f="{interp.get("f_text", "")}"')

    # Store in database
    pattern_data = PatternData(
        pattern=interp['pattern'],
        foundation=interp.get('x_text'),
        final=interp.get('f_text'),
        syllable=interp['matched_text'],
        pattern_id=interp.get('abbrev_id'),
        tags=interp.get('tags')
    )

    syll_id, is_new = syllable_query(pattern_data)
    status = "NEW" if is_new else "EXISTS"
    print(f'    DB: {status} ID={syll_id} - Syllable stored as: "{pattern_data.syllable}"')

    # Verify tone marks are preserved
    if '่' in pattern_data.syllable:
        print(f'    ✓ Tone mark ่ preserved in database')
    print()