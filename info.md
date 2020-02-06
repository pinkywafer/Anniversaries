# Anniversaries

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/pinkywafer/Anniversaries)](https://github.com/pinkywafer/Anniversaries/releases)
![GitHub Release Date](https://img.shields.io/github/release-date/pinkywafer/Anniversaries)
[![GitHub](https://img.shields.io/github/license/pinkywafer/Anniversaries)](LICENSE)

[![Maintenance](https://img.shields.io/badge/Maintained%3F-Yes-brightgreen.svg)](https://github.com/pinkywafer/Anniversaries/graphs/commit-activity)
[![GitHub issues](https://img.shields.io/github/issues/pinkywafer/Anniversaries)](https://github.com/pinkywafer/Anniversaries/issues)

[![Buy me a coffee](https://img.shields.io/static/v1.svg?label=Buy%20me%20a%20coffee&logo=buy%20me%20a%20coffee&logoColor=white&labelColor=ff69b4&message=donate&color=Black)](https://www.buymeacoffee.com/V3q9id4)

[![Support Pinkywafer on Patreon][patreon-shield]][patreon]

The 'anniversaries' component is a Home Assistant custom sensor which counts down to a recurring date such as birthdays, but can be used for any anniversary which occurs annually on the same date.

**1.0.0 includes BREAKING CHANGES** read the [release notes](https://github.com/pinkywafer/anniversaries/releases/latest).

State Returned:

* The number of days remaining to the next occurance.

Attributes:

* years at next anniversary: number of years that will have passed at the next occurrence  _(NOT displayed if year is unknown)_
* current years: number of years have passed since the first occurance (ie, current age)  _(NOT displayed if year is unknown)_
* date:  The date of the first occurence _(or the date of the next occurence if year is unknown)_ (formatted by the date_format attribute if set)
* weeks_remaining: The number of weeks until the anniversary
* unit_of_measurement: 'Days' By default, this is displayed after the state. _this is NOT translate-able.  See below for work-around_

### Notes about unit of measurement

Unit_of_measurement is *not* translate-able.
You can, however, change the unit of measurement with a customization. There are two ways to do this:

* _NOTE that each sensor would require it's own customization_

_This example would replace `Days` with `Dias`_

* In customize.yaml:

    ```yaml
    sensor.your_sensor_id:
      unit_of_measurement: Dias
    ```

* Use the Customizations from the Configuration menu:
  1. Select your sensor
  2. under "Pick an attribute to override" select unit_of_measurement
  3. Type `Dias` in the box
  4. Press save

## Configuration

Anniversaries can be configured on the integrations menu or in configuration.yaml

### Config Flow

In Configuration/Integrations click on the + button, select Anniversaries and configure the options on the form.

### configuration.yaml

Add `anniversaries` sensor in your `configuration.yaml`. The following example adds two sensors - Shakespeare's birthday and wedding anniversary!

```yaml
# Example configuration.yaml entry

anniversaries:
  sensors:
  - name: Shakespeare's Birthday
    date: '1564-04-23'
  - name: Shakespeare's Wedding Anniversary
    date: '1582-11-27'
```

### CONFIGURATION PARAMETERS

|Attribute |Optional|Description
|:----------|----------|------------
| `name` | No | Friendly name
|`date` | No | date in format `'YYYY-MM-DD'` (or `'MM-DD'` if year is unknown)
| `icon_normal` | Yes | Default icon **Default**:  `mdi:calendar-blank`
| `icon_today` | Yes | Icon if the anniversary is today **Default**: `mdi:calendar-star`
| `days_as_soon` | Yes | Days in advance to display the icon defined in `icon_soon` **Default**: 1
| `icon_soon` | Yes | Icon if the anniversary is 'soon' **Default**: `mdi:calendar`
| `date_format` | Yes | formats the returned date **Default**: '%Y-%m-%d' _for reference, see [http://strftime.org/](http://strftime.org/)_

[patreon-shield]: https://c5.patreon.com/external/logo/become_a_patron_button.png
[patreon]: https://www.patreon.com/pinkywafer
