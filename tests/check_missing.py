from get_vowels_multi import get_vowels_multi, load_patterns, get_all_pattern_interpretations

text = 'ญัตติที่เสนอได้ผ่านที่ประชุมด้วยมติเอกฉันท์'

# Check position 17 specifically
print(f'Position 17: "{text[17]}"')

# Load patterns and check what matches at position 17
patterns = load_patterns("thai_vowels_tagged_9-21-2025-2-31-pm.json")

print("Checking patterns at position 17:")
for pattern_data in patterns:
    interpretations = get_all_pattern_interpretations(text, pattern_data, 17)
    if interpretations:
        for interp in interpretations:
            print(f'  Found: {interp["pattern"]} - "{interp["matched_text"]}" Pos: {interp["start_pos"]}-{interp["end_pos"]}')

# Also check positions around 17
for pos in [15, 16, 17, 18, 19]:
    print(f'\nPosition {pos}: "{text[pos]}"')
    found_any = False
    for pattern_data in patterns:
        interpretations = get_all_pattern_interpretations(text, pattern_data, pos)
        if interpretations:
            found_any = True
            for interp in interpretations:
                if 'า' in interp["matched_text"]:
                    print(f'  Found า pattern: {interp["pattern"]} - "{interp["matched_text"]}" Pos: {interp["start_pos"]}-{interp["end_pos"]}')
    if not found_any:
        print(f'  No patterns found at position {pos}')