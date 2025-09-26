# Enhanced Pattern ID System Design

## Dual ID Format

### 1. Abbreviated ID (for quick reference)
Format: `{sound}{length}{openness}{glide}{index}`

Components:
- `sound`: Full sound value (e.g., "a", "ua", "ai")
- `length`: Single letter - "s" (short) or "l" (long)
- `openness`: Single letter - "o" (open) or "c" (closed)
- `glide`: Optional - "jg" (j-glide/ย) or "wg" (w-glide/ว) when present
- `index`: Optional number for duplicates (1, 2, 3...)

Examples:
- `xา` → `alo` (long open a)
- `xาย` → `alcjg` (long closed a with j-glide)
- `xาว` → `alcwg` (long closed a with w-glide)
- `ใx` → `aiscjg1` (short closed ai with j-glide, first variant)
- `ไxย` → `aiscjg2` (short closed ai with j-glide, second variant)

### 2. Long ID (for clarity and debugging)
Format: `{sound}_length{length}_vowel{openness}{_glide}{_index}`

Components:
- `sound`: Full sound value
- `length`: Full word - "short" or "long"
- `openness`: Full word - "open" or "closed"
- `glide`: Optional - "_jglide" or "_wglide" when present
- `index`: Optional "_1", "_2", etc. for duplicates

Examples:
- `xา` → `a_lengthlong_vowelopen`
- `xาย` → `ai_lengthlong_vowelclosed_jglide`
- `xาว` → `aow_lengthlong_vowelclosed_wglide`
- `ใx` → `ai_lengthshort_vowelclosed_jglide_1`
- `ไxย` → `ai_lengthshort_vowelclosed_jglide_2`

## Glide Detection Rules

### J-Glide (glide_j tag or ย ending):
- Pattern ends with `ย` (not as foundation/final marker)
- Has `glide_j` tag

### W-Glide (glide_w tag or ว ending):
- Pattern ends with `ว` (not as foundation/final marker)
- Has `glide_w` tag

## Implementation Notes

1. **Both IDs stored**: Each pattern will have both abbreviated and long IDs
2. **Abbreviated for algorithms**: Fast lookups and compact storage
3. **Long for debugging**: Clear understanding of pattern properties
4. **Database compatibility**: IDs will be added to patterns without modifying existing structure