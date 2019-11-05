# Anniversaries
The 'anniversaries' component is a Home Assistant custom sensor which counts down to a recurring date such as birthdays, but can be used for any anniversary which occurs annually on the same date.

State Returned:
* The number of days remaining to the next occurance.

Attributes:
* years at next anniversary: number of years that will have passed at the next occurrence 
* current years: number of years have passed since the first occurance (ie, age)
* date:  The date as configured

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
---
[<a href="https://www.buymeacoffee.com/V3q9id4" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/purple_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>](https://www.buymeacoffee.com/V3q9id4)
