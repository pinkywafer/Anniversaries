# Jewish Calendar Implementation Summary

## Overview
This document summarizes the implementation of Hebrew/Jewish calendar support for the Anniversaries Home Assistant integration.

## Features Implemented

### 1. Calendar Type Selection
- Added `calendar_type` configuration option with two values:
  - `gregorian` (default) - Standard Gregorian calendar
  - `hebrew` - Hebrew/Jewish calendar

### 2. Hebrew Date Input Formats
Users can now input Hebrew dates in multiple formats:
- **DD-MM-YYYY** (e.g., "15-03-5745") - Full Hebrew date
- **DD-MM** (e.g., "15-03") - Hebrew date without year
- **DD MonthName YYYY** (e.g., "15 Adar 5745") - With month names
- **DD MonthName** (e.g., "15 Adar") - Month name without year

Supported month names (English and Hebrew):
- Tishrei (תשרי), Cheshvan/Marcheshvan (חשוון/מרחשוון)
- Kislev (כסלו), Tevet (טבת), Shevat (שבט)
- Adar (אדר), Adar I / Adar_I (אדר א), Adar II / Adar_II (אדר ב)
- Nisan (ניסן), Iyar (אייר), Sivan (סיוון)
- Tammuz (תמוז), Av (אב), Elul (אלול)

**Note:** For Adar I and Adar II, you can use either spaces (e.g., "15 Adar I 5765") or underscores (e.g., "15 Adar_I 5765").

### 3. Hebrew Calendar Recurrence
Anniversaries using Hebrew calendar now recur on the same Hebrew date each year:
- The system calculates the next occurrence based on the Hebrew calendar
- Properly handles conversion between Hebrew and Gregorian dates
- Updates daily to show correct countdown

### 4. Edge Case Handling

#### Adar in Leap Years
- Follows halachic convention: birthdays in Adar are celebrated in Adar II during leap years
- Adar I birthdays remain in Adar I in leap years
- Non-leap years: all Adar dates use regular Adar (month 6)

#### Variable Month Lengths
- Handles months with 29 or 30 days correctly
- If a date doesn't exist in a particular year (e.g., 30th of a 29-day month), uses the last day of that month

### 5. Display Attributes
New sensor attributes for Hebrew calendar entries:
- `calendar_type`: Shows whether this is "gregorian" or "hebrew"
- `hebrew_date`: Original Hebrew date as entered by user
- `hebrew_next_date`: Next occurrence in Hebrew calendar format (e.g., "15 Adar II 5786")
- Standard attributes (`date`, `next_date`, etc.) still show Gregorian dates for compatibility

### 6. Calendar Integration
Calendar events now include Hebrew date information:
- Event descriptions show both Hebrew and Gregorian dates
- Format: "Hebrew Date: 15-03-5745" and "Next Hebrew Date: 15 Adar II 5786"

### 7. User Interface
Updated config flow to include:
- Calendar Type selector dropdown
- Updated date field descriptions showing format for both calendar types
- Proper validation for each calendar type
- Error messages indicating correct format for selected calendar type

### 8. Translations
Full support in both English and Hebrew:
- English (`en.json`): Calendar type options, updated date descriptions, error messages
- Hebrew (`he.json`): Hebrew translations for all new fields and messages

## Technical Implementation

### Files Modified
1. **manifest.json** - Added `hdate>=0.10.0` dependency
2. **const.py** - Added calendar type constants and Hebrew date validation
3. **sensor.py** - Core Hebrew calendar calculation logic
4. **config_flow.py** - UI for calendar type selection
5. **calendar.py** - Calendar event descriptions with Hebrew dates
6. **translations/en.json** - English translations
7. **translations/he.json** - Hebrew translations

### Key Functions
- `validate_hebrew_date()` - Validates Hebrew date input in various formats
- `_calculate_next_hebrew_anniversary()` - Calculates next occurrence in Hebrew calendar
- `_handle_adar_month()` - Handles Adar month in leap vs. non-leap years
- `_get_max_day_in_month()` - Gets maximum days in a Hebrew month
- `_format_hebrew_date()` - Formats Hebrew date for display

### Dependencies
- **hdate** (py-libhdate) - Python library for Hebrew calendar conversions
  - Same library used by Home Assistant's built-in Jewish Calendar integration
  - Provides accurate Hebrew calendar calculations
  - Handles all edge cases including leap years

## Usage Examples

### Example 1: Hebrew Birthday
```yaml
anniversaries:
  sensors:
  - name: "David's Birthday"
    calendar_type: hebrew
    date: "15-03-5745"  # 15 Adar 5745
```

### Example 2: Yahrzeit (Anniversary of Death)
```yaml
anniversaries:
  sensors:
  - name: "Grandmother's Yahrzeit"
    calendar_type: hebrew
    date: "10 Shevat 5720"
```

### Example 3: Adar I Date (Leap Year Month)
```yaml
anniversaries:
  sensors:
  - name: "Sarah's Birthday"
    calendar_type: hebrew
    date: "15 Adar I 5765"  # Spaces or underscores both work: "15 Adar_I 5765"
```

### Example 4: Hebrew Date Without Year (Recurring)
```yaml
anniversaries:
  sensors:
  - name: "Hebrew Holiday"
    calendar_type: hebrew
    date: "15-07"  # 15 Nisan (Pesach)
    one_time: false
```

### Example 5: Config Flow (UI)
1. Go to Settings → Integrations → Add Integration → Anniversaries
2. Select "Calendar Type": Hebrew
3. Enter date in Hebrew format: "15-03-5745" or "15 Adar 5745" (use "15 Adar I 5765" for Adar I)
4. Configure other options as needed

## Testing Checklist

✅ Gregorian dates still work (backward compatibility)
✅ Hebrew date input formats accepted
✅ Hebrew anniversaries recur on correct Hebrew date each year
✅ Adar handling in leap years follows halachic convention
✅ Display shows Hebrew dates for Hebrew calendar entries
✅ Config flow includes calendar type selector
✅ English and Hebrew translations implemented
✅ Calendar events display Hebrew date information
✅ No linter errors in any modified files
✅ Month name parsing works for both English and Hebrew

## Backward Compatibility
- Existing Gregorian calendar entries continue to work without modification
- Default calendar type is Gregorian
- All existing attributes remain unchanged
- New attributes only added for Hebrew calendar entries

## Future Enhancements (Optional)
- Support for displaying dates in Hebrew script (א׳ באדר ה׳תשמ״ה)
- Integration with Home Assistant's Jewish Calendar for holiday awareness
- Support for other calendar systems (Islamic, Persian, etc.)
- Half-anniversary support for Hebrew calendar dates

## Notes
- Hebrew calendar years are typically 5700+ (current era is 5780s)
- The system uses py-libhdate for accurate conversions
- All Hebrew dates are converted to Gregorian internally for calculation
- Display can show both Hebrew and Gregorian formats
