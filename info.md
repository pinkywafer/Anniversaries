# Anniversaries

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/pinkywafer/Anniversaries)](https://github.com/pinkywafer/Anniversaries/releases)
![GitHub Release Date](https://img.shields.io/github/release-date/pinkywafer/Anniversaries)
[![GitHub](https://img.shields.io/github/license/pinkywafer/Anniversaries)](LICENSE)

[![Maintenance](https://img.shields.io/badge/Maintained%3F-Yes-brightgreen.svg)](https://github.com/pinkywafer/Anniversaries/graphs/commit-activity)
[![GitHub issues](https://img.shields.io/github/issues/pinkywafer/Anniversaries)](https://github.com/pinkywafer/Anniversaries/issues)

[![Buy me a coffee](https://img.shields.io/static/v1.svg?label=Buy%20me%20a%20coffee&logo=buy%20me%20a%20coffee&logoColor=white&labelColor=ff69b4&message=donate&color=Black)](https://www.buymeacoffee.com/V3q9id4)

The 'anniversaries' component is a Home Assistant custom sensor which counts down to a recurring date such as birthdays, but can be used for any anniversary which occurs annually on the same date.

State Returned:
* The number of days remaining to the next occurance.

Attributes:
* years at next anniversary: number of years that will have passed at the next occurrence 
* current years: number of years have passed since the first occurance (ie, age)
* date:  The configured date (formatted by the date_format attribute if set)

## Configuration
Add `anniversaries` sensor in your `configuration.yaml`. The following example adds two sensors - Shakespeare's birthday and wedding anniversary!
### CONFIGURATION PARAMETERS
|Attribute |Optional|Description
|:----------|----------|------------
|`platform` | No |`anniversaries`
|`date` | No | date in format `'YYYY-MM-DD'`
| `icon_normal` | Yes | Default icon **Default**:  `mdi:calendar-blank`
| `icon_today` | Yes | Icon if the anniversary is today **Default**: `mdi:calendar-star`
| `icon_tomorrow` | Yes | Icon if the anniversary is tomorrow **Default**: `mdi:calendar`
| `date_format` | Yes | formats the returned date **Default**: '%Y-%m-%d' _for reference, see [http://strftime.org/](http://strftime.org/)_

```yaml
# Example configuration.yaml entry
sensor:
  - platform: anniversaries
    name: Shakespeare's Birthday
    date: '1564-04-23'
  - platform: anniversaries
    name: Shakespeare's Wedding Anniversary
    date: '1582-11-27'
```
