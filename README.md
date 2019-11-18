# Anniversaries
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/pinkywafer/Anniversaries)](https://github.com/pinkywafer/Anniversaries/releases)
![GitHub Release Date](https://img.shields.io/github/release-date/pinkywafer/Anniversaries)
[![GitHub](https://img.shields.io/github/license/pinkywafer/Anniversaries)](LICENSE)

[![Maintenance](https://img.shields.io/badge/Maintained%3F-Yes-brightgreen.svg)](https://github.com/pinkywafer/Anniversaries/graphs/commit-activity)
[![GitHub issues](https://img.shields.io/github/issues/pinkywafer/Anniversaries)](https://github.com/pinkywafer/Anniversaries/issues)

[![Buy me a coffee](https://img.shields.io/static/v1.svg?label=Buy%20me%20a%20coffee&logo=buy%20me%20a%20coffee&logoColor=white&labelColor=ff69b4&message=donate&color=Black)](https://www.buymeacoffee.com/V3q9id4)

The 'anniversaries' component is a Home Assistant custom sensor which counts down to a recurring date such as birthdays, but can be used for any anniversary which occurs annually on the same date.

**1.0.0 includes BREAKING CHANGES** read the [release notes](https://github.com/pinkywafer/anniversaries/releases/latest).

State Returned:
* The number of days remaining to the next occurance.

Attributes:
* years at next anniversary: number of years that will have passed at the next occurrence 
* current years: number of years have passed since the first occurance (ie, age)
* date:  The configured date (formatted by the date_format attribute if set)

## Table of Contents
* [Installation](#installation)
  + [Manual Installation](#manual-installation)
  + [Installation via HACS](#installation-via-hacs)
* [Configuration](#configuration)
  + [Configuration Parameters](#configuration-parameters)
* [State and Attributes](#state-and-attributes)

## Installation

### MANUAL INSTALLATION
1. Download the `anniversaries.zip` file from the 
   [latest release](https://github.com/pinkywafer/anniversaries/releases/latest).
2. Unpack the release and copy the `custom_components/anniversaries` directory
   into the `custom_components` directory of your Home Assistant
   installation.
3. Configure the `anniversaries` sensor.
4. Restart Home Assistant.

### INSTALLATION VIA HACS
1. Ensure that [HACS](https://custom-components.github.io/hacs/) is installed.
2. Search for and install the "anniversaries" integration.
3. Configure the `anniversaries` sensor.
4. Restart Home Assistant.

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
  - platform: anniversaries
    name: Shakespeare's Birthday
    date: '1564-04-23'
  - platform: anniversaries
    name: Shakespeare's Wedding Anniversary
    date: '1582-11-27'
```

### CONFIGURATION PARAMETERS
|Attribute |Optional|Description
|:----------|----------|------------
| `name` | No | Friendly name
|`date` | No | date in format `'YYYY-MM-DD'`
| `icon_normal` | Yes | Default icon **Default**:  `mdi:calendar-blank`
| `icon_today` | Yes | Icon if the anniversary is today **Default**: `mdi:calendar-star`
| `days_as_soon` Yes | Days in advance to display the icon defined in `icon_soon` **Default**: 1
| `icon_soon` | Yes | Icon if the anniversary is tomorrow **Default**: `mdi:calendar`
| `date_format` | Yes | formats the returned date **Default**: '%Y-%m-%d' _for reference, see [http://strftime.org/](http://strftime.org/)_
