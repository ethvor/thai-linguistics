#!/usr/bin/env python3
"""
Thai Character Rendering Logic
Handles character grouping, combining marks, and HTML generation
"""

def is_combining_character(char):
    """
    Check if a character is a Thai combining mark

    Combining ranges:
    - 0x0E31-0x0E3A: vowels and tone marks that appear above/below base
    - 0x0E47-0x0E4E: additional diacritics
    """
    char_code = ord(char)
    return (0x0E31 <= char_code <= 0x0E3A) or (0x0E47 <= char_code <= 0x0E4E)


def is_below_baseline(char):
    """
    Check if a combining character appears below the baseline

    Below baseline: 0x0E38-0x0E3A (ุ ู ฺ)
    """
    char_code = ord(char)
    return 0x0E38 <= char_code <= 0x0E3A


def group_characters(classifications):
    """
    Group base characters with their combining marks

    Args:
        classifications: List of dicts with 'index', 'char', 'class', 'avp'

    Returns:
        List of character groups, where each group is:
        {
            'base': {'index': int, 'char': str, 'class': str, 'avp': bool},
            'combining_above': [list of combining chars with stack levels],
            'combining_below': [list of combining chars with stack levels],
            'is_orphaned': bool  # True if this is an orphaned combining mark
        }
    """
    groups = []
    i = 0

    while i < len(classifications):
        item = classifications[i]

        # Check if this is a combining character
        if is_combining_character(item['char']):
            # Orphaned combining mark - create group with dotted circle
            groups.append({
                'base': {
                    'index': item['index'],
                    'char': '\u25CC' + item['char'],  # ◌ + combining mark
                    'class': item['class'],
                    'avp': item['avp']
                },
                'combining_above': [],
                'combining_below': [],
                'is_orphaned': True
            })
            i += 1
            continue

        # Start a new group with this base character
        group = {
            'base': item,
            'combining_above': [],
            'combining_below': [],
            'is_orphaned': False
        }

        # Look ahead for combining characters
        j = i + 1
        above_count = 0
        below_count = 0

        while j < len(classifications):
            next_item = classifications[j]

            if is_combining_character(next_item['char']):
                # Add stack level to the combining character
                combining_char = {
                    'index': next_item['index'],
                    'char': next_item['char'],
                    'class': next_item['class'],
                    'avp': next_item['avp']
                }

                if is_below_baseline(next_item['char']):
                    combining_char['stack_level'] = below_count
                    group['combining_below'].append(combining_char)
                    below_count += 1
                else:
                    combining_char['stack_level'] = above_count
                    group['combining_above'].append(combining_char)
                    above_count += 1

                j += 1
            else:
                # Not a combining character, stop looking
                break

        groups.append(group)
        i = j

    return groups


def generate_html_markup(groups, toggles):
    """
    Generate HTML markup from character groups

    Args:
        groups: List of character groups from group_characters()
        toggles: Dict of class names to boolean (show highlighting)
            e.g., {'tan': True, 'sara': True, 'yuk': True, 'kho_yok_waen': True}

    Returns:
        HTML string with complete markup
    """
    html_parts = []

    for group in groups:
        # Start character group
        html_parts.append('<span class="char-group">')

        # Render base character
        base = group['base']
        show_highlight = toggles.get(base['class'], False)
        css_class = base['class'] if show_highlight else ''

        html_parts.append(f'<span class="char-base {css_class}">{base["char"]}</span>')

        # Render combining characters above baseline (as siblings to base)
        for combining in group['combining_above']:
            show_highlight = toggles.get(combining['class'], False)
            css_class = combining['class'] if show_highlight else ''
            stack_level = combining['stack_level']
            html_parts.append(
                f'<span class="char-combining char-above-{stack_level} {css_class}">'
                f'{combining["char"]}</span>'
            )

        # Render combining characters below baseline (as siblings to base)
        for combining in group['combining_below']:
            show_highlight = toggles.get(combining['class'], False)
            css_class = combining['class'] if show_highlight else ''
            stack_level = combining['stack_level']
            html_parts.append(
                f'<span class="char-combining char-below-{stack_level} {css_class}">'
                f'{combining["char"]}</span>'
            )

        # Close character group
        html_parts.append('</span>')

    return ''.join(html_parts)


def render_thai_text(classifications, toggles=None):
    """
    Complete rendering pipeline: classify → group → generate HTML

    Args:
        classifications: List of character classifications from classify_text()
        toggles: Optional dict of highlighting toggles (defaults to all True)

    Returns:
        HTML string ready to display
    """
    # Default: show all highlighting
    if toggles is None:
        toggles = {
            'tan': True,
            'sara': True,
            'yuk': True,
            'diacritic': True,
            'kho_yok_waen': True,
            'unsure': True
        }

    # Group characters with combining marks
    groups = group_characters(classifications)

    # Generate HTML markup
    html = generate_html_markup(groups, toggles)

    return html


def transform_intermediate_classifications(classifications):
    """
    Transform classifications for intermediate step (implements Extended IFTC):
    - Remove all yuk (tone marks) and diacritic marks
    - Replace tan with "x" if it has a yuk OR sara mark (terminal), otherwise "a"
    - Keep sara (vowels) and exceptions as-is

    Extended IFTC: If any consonant has a vowel part OR tone mark, then it is
    a terminal initial-foundation consonant.

    Args:
        classifications: List of character classifications

    Returns:
        Modified classifications list (same format as input)
    """
    # First, group to see which tan have yuk or sara above/below them
    groups = group_characters(classifications)

    result = []
    for group in groups:
        base = group['base']

        # Skip if base is yuk or diacritic (orphaned combining mark)
        if base['class'] in ('yuk', 'diacritic'):
            continue

        # Copy the base item
        new_item = base.copy()

        # If tan, check if it has yuk OR sara (Extended IFTC)
        if base['class'] == 'tan':
            has_vowel_or_tone = any(
                c['class'] in ('yuk', 'sara')
                for c in group['combining_above'] + group['combining_below']
            )
            new_item['char'] = 'x' if has_vowel_or_tone else 'a'

        result.append(new_item)

        # Add combining sara (above and below), but skip yuk and diacritics
        for combining in group['combining_above']:
            if combining['class'] not in ('yuk', 'diacritic'):
                result.append(combining.copy())

        for combining in group['combining_below']:
            if combining['class'] not in ('yuk', 'diacritic'):
                result.append(combining.copy())

    return result
