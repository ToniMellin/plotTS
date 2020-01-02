# plotTS
Easy plotting GUI to use plotly in creating plots from data files (.csv or .xlsx)

![2019-12-30 19_08_55-Window](https://user-images.githubusercontent.com/55407190/71592172-ebf32e80-2b37-11ea-9a77-58ed20d9efa7.png)

![example](https://user-images.githubusercontent.com/55407190/71592026-417b0b80-2b37-11ea-97d3-f90072f71c21.png)

## Installation

Clone the repository

Install needed libraries to python 3.7 with pip: 

```
pip install -r requirements.txt
```

## Features

### 1.2.0 / 1.2.1
- Convert time x-axis to datetime object as per given format
- Automatic time x-axis conversion option for certain formats
- Updated plotTS.py independent examples

### 1.1.0
- Save plot as HTML file
- plotTS.py independent examples

### 1.0.1
- Drag and drop file insert
- Load column names
- Select X-, Y- and Y2-Axis items
- Plot the data
- Change plot visual appearance (markers and line)
- Add rolling average
- Save and Load presets
- Debugging file creation

## Usage:

### GUI usage

#### Basic usage
Start using by running pTS_GUI.py

Give a file location by dragging and dropping to the "blue" area or select by pressing 'File'

Load File to get column names

Select wanted X-axis and Y-axis and/or Y2-axis (use **Shift** and **Ctrl** to select multiple or certain columns)

Press Plot

#### Settings
Go to settings tab

Select any wanted options:
- Convert x-axis time to datetime (will try to convert selected x-axis)
  - Auto: Tries to automatically convert the x-axis time to datetime
    - Formats that Auto can detect:
  - Manual: Converts x-axis time based on the given time format
  - Off: No action to x-axis, if time format is not in ISO format ('%Y-%m-%d %H:%M:%S' or '%Y-%m-%dT%H:%M:%SZ') plotly can't automatically detect it and can't use the timestamps effectively
  - The reason for using this functionality is mainly if the timestamps of your x-axis are not evenly distributed, plotly can't interpret that and thus your the plotted  data will not actually match the real data and will be distorted 
- Plot trace mode
  - Lines+Markers plots lines between datapoints and shows markers for datapoints
  - Lines plots only lines between datapoints
  - Markers plots only markers on datapoints
- Add Averaging Curves (rolling average)
  - On: Adds new additional average curves for all selected Y and Y2 axis elements based on selected rolling average number
  - Off: Feature off

**Auto Time Formats**
The **Auto** option for x-axis time goes through the below datetime formats:
- '%Y-%m-%d %H:%M:%S',
- '%Y-%m-%dT%H:%M:%S',
- '%Y-%m-%dT%H:%M:%SZ',
- '%Y-%m-%d %H:%M',
- '%Y/%m/%d %H:%M:%S',
- '%Y/%m/%d %H:%M',
- '%d/%m/%Y %H:%M:%S',
- '%d/%m/%Y %H:%M',
- '%H:%M:%S %d-%m-%Y',
- '%H:%M %d-%m-%Y',
- '%H:%M:%S %d/%m/%Y',
- '%H:%M %d/%m/%Y'

If none of them are a match it will still try a non date time conversion, which assumes a time format separated by colon ':', also accepting milliseconds. Thus below time formats should be recognized and changed to timedelta objects (which plotly can identify and use properly) in the internal dataframe before plotting:
- 123:22:14.123 *(123 hours, 22 minutes, 14 seconds, 123 milliseconds)*
- 123:22:14 *(123 hours, 22 minutes, 14 seconds)*
- 123:22 *(123 hours, 22 minutes)*
- 23:22 *(23 hours, 22 minutes)*



#### Presets
Presets can save your selected axis elements and also the settings to reduce needing to redo these actions on files that are formatted exactly the same, making plotting of frequently replicated files easy

You can also share presets you made to others by copying your presets.ini and others replacing theirs with that one

**Save Settings:**
1. Load your file
2. Select wanted axis elements
3. Go to Settings tab
4. Select wanted settings
5. Input preset name
6. Press Save

You should be able to see the saved preset with the inputted name in the presets list and the preset will also be saved to the presets.ini

**Load Settings:**
1. Load your file
2. Select the wanted preset from the presets list
3. Press Load

All the settings and axis elements should be now loaded and you are ready to plot or save as HTML

**In case of issues**
If for some reason you get errors using the presets you can see if you can fix the presets file by editing it with notepad++ or start fresh by simply deleting the presets.ini, if the pTS_GUI is started without presets.ini existing, it will create a new blank presets file

### plotTS.py independent usage
Run plotTS.py independently (mainly for learning, so others can learn to use the main libraries such as pandas and plotly by themselves)

ploTS.py will run as main and execute the examples

it will create exampledata.csv and plot that, as well as save_example.html

Edit and explore how plotly works and how pandas is utilized!

