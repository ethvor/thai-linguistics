from get_vowels_multi import load_patterns, get_all_pattern_interpretations

text = 'ญัตติที่เสนอได้ผ่านที่ประชุมด้วยมติเอกฉันท์'

# The sequence around position 17 is: ผ่าน
# Position 15: ผ
# Position 16: ่ (tone mark)
# Position 17: า (vowel mark)
# Position 18: น

print('Text around position 17:')
for i in range(14, 20):
    print(f'  {i}: "{text[i]}"')

print('\nChecking xา pattern specifically:')
patterns = load_patterns("thai_vowels_tagged_9-21-2025-2-31-pm.json")

for pattern_data in patterns:
    if pattern_data.get('pattern') == 'xา':
        print(f'Found xา pattern: {pattern_data}')

        # Try matching at various positions
        for pos in range(14, 18):
            interpretations = get_all_pattern_interpretations(text, pattern_data, pos)
            if interpretations:
                for interp in interpretations:
                    print(f'  Match at pos {pos}: "{interp["matched_text"]}" x="{interp.get("x_text")}"')
            else:
                print(f'  No match at pos {pos}')

# Check if we have any pattern that can handle tone marks
print('\nChecking patterns with tone marks:')
for pattern_data in patterns:
    pattern = pattern_data.get('pattern', '')
    if '่' in pattern or 'x' in pattern and 'า' in pattern:
        print(f'Potential pattern: {pattern}')