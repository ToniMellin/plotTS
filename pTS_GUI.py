from appJar import gui
import os
import logging
import sys
import plotTS as pTS
from configparser import ConfigParser

version = '1.4.0'
print("\nplotTS {}\n".format(version))

#logging configuration
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

#GUI initialization part
ui = gui("plotTS {}".format(version), "650x750") #, useTtk=True)
#ui.setTtkTheme('winnative')
ui.increaseButtonFont()
ui.setFont(11)
ui.setFg('Black', override=False)
ui.setBg('darkgray', override=False, tint=False)
ui.resizable = True

#appJar UI logging settings
ui.setLogLevel('DEBUG')

#locate preset id based on selected preset name
def findPresetID(name):
    for section in config:
        if config[section].get('name') == name:
            pres_id = config[section].get('id')
            ui.debug('Preset ID %(id)s located for preset name %(presName)s', {'id': pres_id, 'presName': name})
            return pres_id
    ui.error('could not find name from presets to match for id')
    ui.queueFunction(ui.setLabel, 'output', 'Issue with preset: {}!!!'.format(name))
    ui.queueFunction(ui.setLabelBg, 'output', 'red')
    return False

#TODO add data cleaning options
#collect and change preset values in config and then save the presets to preset.ini
def changePresetValues(oldName, newName):
    preset_id = int(findPresetID(oldName))
    presetSec = presetSectionValues[preset_id-1]
    config.set(presetSec, 'name', newName)
    try:
        #collect axis options, marker trace, averaging and save to config
        listBoxes = ui.getAllListBoxes()
        ui.debug('listBoxes: %s', listBoxes)
        x_items = listBoxes['X-Axis']
        config.set(presetSec, 'x_axis', ','.join(x_items))
        y_items = listBoxes['Y-Axis']
        config.set(presetSec, 'y_axis', ','.join(y_items))
        y2_items = listBoxes['Y2-Axis']
        config.set(presetSec, 'y2_axis', ','.join(y2_items))
        #load timeconvert settings
        timeconvert_mode = ui.getRadioButton('timeconvert')
        config.set(presetSec, 'timeconvert_mode', timeconvert_mode)
        ui.debug('timeconvert_mode: %s', timeconvert_mode)
        timeconvert_format =  ui.getEntry('Time format:')
        config.set(presetSec, 'timeconvert_format', timeconvert_format)
        ui.debug('timeconvert_format: %s', timeconvert_format)
        #Trace settings
        trace_mode = ui.getRadioButton('trace_mode')
        trace_mode_id = convertTraceModeToID(trace_mode)
        trace_conf = str(trace_mode_id)
        config.set(presetSec, 'marker_trace', trace_conf)
        ui.debug('trace_mode_id: %s', trace_conf)
        averageButton = ui.getRadioButton('average')
        ui.debug('average button is %s', averageButton)
        config.set(presetSec, 'avg_on', averageButton)
        average_rollNum = ui.getSpinBox('average_rollNum')
        ui.debug('average roll num: %s', average_rollNum)
        config.set(presetSec, 'avg_rollnum', average_rollNum)
        writeToConfig() #save config
        #change UI preset naming
        ui.renameOptionBoxItem('Preset:', oldName, newName, callFunction=False)
        #add info of changes
        ui.info('Preset %(pres)s name changed to -> %(name)s', {'pres': presetSec, 'name': newName})
        ui.info('Preset %(pres)s x-axis changed to -> %(axisInfo)s', {'pres': presetSec, 'axisInfo': x_items})
        ui.info('Preset %(pres)s y-axis changed to -> %(axisInfo)s', {'pres': presetSec, 'axisInfo': y_items})
        ui.info('Preset %(pres)s y2-axis changed to -> %(axisInfo)s', {'pres': presetSec, 'axisInfo': y2_items})
        ui.info('Preset %(pres)s timeconvert_mode changed to -> %(time_mode)s', {'pres': presetSec, 'time_mode': timeconvert_mode})
        ui.info('Preset %(pres)s timeconvert_format changed to -> %(time_format)s', {'pres': presetSec, 'time_format': timeconvert_format})
        ui.info('Preset %(pres)s markers changed to -> %(traceInfo)s', {'pres': presetSec, 'traceInfo': trace_mode})
        ui.info('Preset %(pres)s average mode changed to -> %(averageInfo)s', {'pres': presetSec, 'averageInfo': averageButton})
        ui.info('Preset %(pres)s average rolling number changed to -> %(avgRollInfo)s', {'pres': presetSec, 'avgRollInfo': average_rollNum})
        ui.info('Preset %s saved', presetSec)
        ui.queueFunction(ui.setLabel, 'output', 'Saved preset: {}'.format(newName))
        ui.queueFunction(ui.setLabelBg, 'output', 'yellow')
    except Exception as e:
        ui.critical('%s', e)
        ui.error('Cannot save preset %(new)s to %(old)s', {'new': newName, 'old': presetSec})
        ui.queueFunction(ui.setLabel, 'output', 'ERROR saving preset {}!!! Possible that presets.ini corrupted!!!'.format(newName))
        ui.queueFunction(ui.setLabelBg, 'output', 'red')

#check if preset is empty
def checkIfPresetDataEmpty(presetSec):
    dataCount = 0
    if config[presetSec].get('x_axis'):
        dataCount += 1
    if config[presetSec].get('y_axis'):
        dataCount += 1
    if config[presetSec].get('y2_axis'):
        dataCount += 1
    
    if dataCount == 0:
        return True
    else:
        return False

#TODO add data cleaning options
#load preset settings
def loadPresetSettings(presetName):
    preset_id = int(findPresetID(presetName))
    presetSec = presetSectionValues[preset_id-1]
    #check preset for emptydata
    presetEmpty = checkIfPresetDataEmpty(presetSec)
    if presetEmpty == True:
        ui.error('Preset load failed!!... Preset has no values...')
        ui.queueFunction(ui.setLabel, 'output', 'Preset {} is empty!!!'.format(presetName))
        ui.queueFunction(ui.setLabelBg, 'output', 'red')
        return
    #load axis settings from preset
    x_items = config[presetSec].get('x_axis')
    x_itemsList = x_items.split(',')
    y_items = config[presetSec].get('y_axis')
    y_itemsList = y_items.split(',')
    y2_items = config[presetSec].get('y2_axis')
    y2_itemsList = y2_items.split(',')
    #check to see if matches found from the loaded file
    listItems = ui.getAllListItems('X-Axis')
    ui.debug('listItems: %s', listItems)
    xCount = 0
    yCount = 0
    y2Count = 0
    for x_item in x_itemsList:
        for item in listItems:
            if x_item == item:
                xCount+=1
    for y_item in y_itemsList:
        for item in listItems:
            if y_item == item:
                yCount+=1
    for y2_item in y2_itemsList:
        for item in listItems:
            if y2_item == item:
                y2Count+=1
    ui.debug('Preset xCount = %(x_C)s, yCount = %(y_C)s and y2Count = %(y2_C)s', {'x_C': str(xCount), 'y_C': str(yCount), 'y2_C': str(y2Count)})
    #stop loading if no matches in the 
    if listItems == []:
        ui.error('No file loaded!!... Cannot match againts presets lists...')
        ui.queueFunction(ui.setLabel, 'output', 'No file loaded!!... Cannot Load Preset!!!')
        ui.queueFunction(ui.setLabelBg, 'output', 'red')
    elif xCount == 0 and yCount == 0 and y2Count == 0:
        ui.error('Preset load failed!!... No matches to Axis lists...')
        ui.queueFunction(ui.setLabel, 'output', 'Preset {} does not match file!!!'.format(presetName))
        ui.queueFunction(ui.setLabelBg, 'output', 'red')
    else:
        try:
            #change axis options to UI
            ui.deselectAllListItems('X-Axis', callFunction=False)
            for item in x_itemsList:
                ui.selectListItem('X-Axis', item, callFunction=True)
                ui.debug('selected %s in X-Axis', item)
            ui.deselectAllListItems('Y-Axis', callFunction=False)
            for item in y_itemsList:
                ui.selectListItem('Y-Axis', item, callFunction=True)
                ui.debug('selected %s in Y-Axis', item)
            ui.deselectAllListItems('Y2-Axis', callFunction=False)
            for item in y2_itemsList:
                ui.selectListItem('Y2-Axis', item, callFunction=True)
                ui.debug('selected %s in Y2-Axis', item)
            #load time conversion settings
            timeconvert_mode_Set = config[presetSec].get('timeconvert_mode')
            ui.setRadioButton("timeconvert", timeconvert_mode_Set, callFunction=True)
            ui.debug('set timeconvert_mode as %s', timeconvert_mode_Set)
            timeconvert_format_Set = config[presetSec].get('timeconvert_format')
            ui.setEntry("Time format:", timeconvert_format_Set, callFunction=True)
            ui.debug('set timeconvert_format as %s', timeconvert_format_Set)
            #load and set marker settings
            markerSet = config[presetSec].get('marker_trace')
            if markerSet == '1':
                ui.setRadioButton("trace_mode", "Lines+Markers", callFunction=True)
                ui.debug('set marker trace as %s', "Lines+Markers")
            elif markerSet == '2':
                 ui.setRadioButton("trace_mode", "Lines", callFunction=True)
                 ui.debug('set marker trace as %s', "Lines")
            elif markerSet == '3':
                ui.setRadioButton("trace_mode", "Markers", callFunction=True)
                ui.debug('set marker trace as %s', "Markers")
            #load and set averaging settings
            avg_ON = config[presetSec].get('avg_on')
            ui.setRadioButton("average", avg_ON, callFunction=True)
            ui.debug('set averaging %s', avg_ON)
            avg_rollNum = config[presetSec].get('avg_rollnum')
            ui.setSpinBox('average_rollNum', int(avg_rollNum), callFunction=True)
            ui.debug('set average rolling as %s', avg_rollNum)
            #set outputs after loading all settings
            ui.info('Preset %(pres)s loaded as %(name)s', {'pres': presetSec, 'name': presetName})
            ui.queueFunction(ui.setLabel, 'output', 'Loaded preset: {}'.format(presetName))
            ui.queueFunction(ui.setLabelBg, 'output', 'yellow')
        except Exception as e:
            ui.critical('%s', e)
            ui.error('Issue setting axis items')
            ui.queueFunction(ui.setLabel, 'output', 'Issue loading preset: {}'.format(presetName))
            ui.queueFunction(ui.setLabelBg, 'output', 'red')

#save config to preset.ini
def writeToConfig():
    with open('presets.ini', 'w', encoding='utf-8') as config_file:
        config.write(config_file)

#change trace_mode values to correct format
def convertTraceModeToID(trace_mode):
    if trace_mode == 'Lines+Markers':
        trace_mode_id = 1
    elif trace_mode == 'Lines':
        trace_mode_id = 2
    elif trace_mode == 'Markers':
        trace_mode_id = 3
    return trace_mode_id

#loading plot settings from UI to generate the plot
def loadPlotSettings():
    ui.info('Retrieving plotting settings')
    listBoxes = ui.getAllListBoxes()
    try:
        x_items = listBoxes['X-Axis']
        ui.info('Plot X-Axis: %s', x_items)
        y_items = listBoxes['Y-Axis']
        ui.info('Plot Y-Axis: %s', y_items)
        y2_items = listBoxes['Y2-Axis']
        ui.info('Plot Y2-Axis: %s', y2_items)
        if not y2_items: 
            sec_y = False
            ui.debug('NO Secondary axis items selected')
        else:
            sec_y = True
            ui.debug('Secondary axis items selected')
        timeconvert_mode = ui.getRadioButton('timeconvert')
        timeconvert_format =  ui.getEntry('Time format:')
        trace_mode = ui.getRadioButton('trace_mode')
        trace_mode_id = convertTraceModeToID(trace_mode)
        averageButton = ui.getRadioButton('average')
        average_rollNum = ui.getSpinBox('average_rollNum')
        if averageButton == 'On':
            averageMode = True
            y_keyList = []
            y_keyList.extend(y_items)
            for y_item in y_items:
                y_keyList.append('{}_avg={}'.format(y_item, average_rollNum))
            y2_keyList = []
            y2_keyList.extend(y2_items)
            for y2_item in y2_items:
                y2_keyList.append('{}_avg={}'.format(y2_item, average_rollNum))
            ui.info('Added y-axis average data keys: %s', y_keyList)
            ui.info('Added y2-axis average data keys: %s', y2_keyList)
        else:
            averageMode = False
            y_keyList = ''
            y2_keyList = ''
        return x_items, y_items, y_keyList, y2_items, y2_keyList, sec_y, timeconvert_mode, timeconvert_format, trace_mode_id, averageMode, int(average_rollNum)
    except Exception as e:
        ui.critical('%s', e)
        ui.error('ERROR!! Cannot retrieve settings for plotting!')
        ui.queueFunction(ui.setLabel, 'output', 'ERROR retrieving settings')
        ui.queueFunction(ui.setLabelBg, 'output', 'red')
    
#data drop function to set file location based on data drop
def externalDrop(data):
    if data[0] == '{':
        ofile = data.split('{', 1)[1].split('}')[0]
    else:
        ofile = data
    ui.info('Data drop used: %s', ofile)
    ui.setEntry('file', ofile, callFunction=True)

#TODO add data cleaning options
#button press actions
def press(btn):
    ui.info('User pressed --> %s', btn)
    if btn == 'Plot':
        #plot the data based on given datafile, axis options and settings
        try:
            ifile2 = ui.getEntry('file')
            df_inputfile = pTS.inputFiletoDF(ifile2)
            x_items, y_items, y_keyList, y2_items, y2_keyList, sec_y, time_mode, time_format, trace_mode_id, averageMode, average_Num = loadPlotSettings()
            if time_mode == 'Auto':
                try:
                    df2 = pTS.autoConvertTimeValues(df_inputfile, x_items[0])
                except Exception as e:
                    ui.critical('%s', e)
                    ui.error('ERROR!! Auto Correction for timestamps not possible!!!')
                    raise ValueError('Could not convert timestamp automatically!!')
            if time_mode == 'Manual':
                try:
                    df2 = pTS.convertTimeValues(df_inputfile, x_items[0], time_format)
                except Exception as e:
                    ui.critical('%s', e)
                    ui.error('ERROR!! Manual Correction for timestamps not possible!!!')
                    raise ValueError('Could not convert timestamp automatically!!')
            else:
                df2 = df_inputfile
            if averageMode == True:
                df2 = pTS.addAverageData(df2, y_items, y2_items, average_Num) #add average curves with the function
                try:
                    plotDict = pTS.createPlotDict(df2, y_keyList, y2_keyList, trace_mode_id)
                except Exception as e:
                    ui.critical('%s', e)
                    ui.error('ERROR!! Cannot create dictionary for plotting including the averaging!!!')
            else:
                try:
                    plotDict = pTS.createPlotDict(df2, y_items, y2_items, trace_mode_id)
                except Exception as e:
                    ui.critical('%s', e)
                    ui.error('ERROR!! Cannot create dictionary for plotting!!!')
            pTS.createFig(sec_y, plotDict, df2[x_items[0]], df2)
            ui.info('Plotting figure completed!')
            ui.queueFunction(ui.setLabel, 'output', 'Plotting figure completed!')
            ui.queueFunction(ui.setLabelBg, 'output', 'green')
        except ValueError:
            ui.error("Could not timeconvert time X-Axis for plotting!")
            ui.queueFunction(ui.setLabel, 'output', 'Could not convert timestamps of X-Axis for plotting!')
            ui.queueFunction(ui.setLabelBg, 'output', 'red')
        except Exception as e:
            ui.critical('%s', e)
            ui.error("Issues with plotting")
            ui.queueFunction(ui.setLabel, 'output', 'ERROR plotting!!!')
            ui.queueFunction(ui.setLabelBg, 'output', 'red')
    elif btn == 'Save As HTML':
        #similar to plot except save the output as html file
        save_location = ui.getEntry('output_location')
        ui.debug('Save location given: %s', save_location)
        HTML_entry = ui.getEntry('HTML filename')
        ui.debug('HTML filename given: %s', HTML_entry)
        if not save_location:
            ui.setFocus('output_location')
            ui.error('No save directory given to save as HTML!!')
            ui.queueFunction(ui.setLabel, 'output', 'Need save directory to save as HTML...')
            ui.queueFunction(ui.setLabelBg, 'output', 'yellow')
            return
        if not HTML_entry:
            ui.setFocus('HTML filename')
            ui.error('No filename given to save as HTML!!')
            ui.queueFunction(ui.setLabel, 'output', 'Need filename to save as HTML...')
            ui.queueFunction(ui.setLabelBg, 'output', 'yellow')
            return
        else:
            if HTML_entry.endswith('.html'):
                HTML_split = HTML_entry.split('.')
                HTML_name = HTML_split[0]
            else:
                HTML_name = HTML_entry     
        try:
            ifile2 = ui.getEntry('file')
            df_inputfile = pTS.inputFiletoDF(ifile2)
            x_items, y_items, y_keyList, y2_items, y2_keyList, sec_y, time_mode, time_format, trace_mode_id, averageMode, average_Num = loadPlotSettings()
            if time_mode == 'Auto':
                try:
                    df2 = pTS.autoConvertTimeValues(df_inputfile, x_items[0])
                except Exception as e:
                    ui.critical('%s', e)
                    ui.error('ERROR!! Auto Correction for timestamps not possible!!!')
                    raise Exception('%s', e)
            if time_mode == 'Manual':
                try:
                    df2 = pTS.convertTimeValues(df_inputfile, x_items[0], time_format)
                except Exception as e:
                    ui.critical('%s', e)
                    ui.error('ERROR!! Manual Correction for timestamps not possible!!!')
                    raise Exception('%s', e)
            else:
                df2 = df_inputfile
            if averageMode == True:
                df2 = pTS.addAverageData(df2, y_items, y2_items, average_Num) #add average curves with the function
                try:
                    plotDict = pTS.createPlotDict(df2, y_keyList, y2_keyList, trace_mode_id)
                except Exception as e:
                    ui.critical('%s', e)
                    ui.error('ERROR!! Cannot create dictionary for plotting including the averaging!!!')
            else:
                try:
                    plotDict = pTS.createPlotDict(df2, y_items, y2_items, trace_mode_id)
                except Exception as e:
                    ui.critical('%s', e)
                    ui.error('ERROR!! Cannot create dictionary for plotting!!!')
            pTS.saveFigAsHTML(sec_y, plotDict, df2[x_items[0]], df2, os.path.join(save_location, HTML_name))
            ui.info('Saving figure as HTML completed!')
            ui.queueFunction(ui.setLabel, 'output', 'Saving figure as HTML completed!')
            ui.queueFunction(ui.setLabelBg, 'output', 'green')
        except Exception as e:
            ui.critical('%s', e)
            ui.error("Issues with Saving as HTML file")
            ui.queueFunction(ui.setLabel, 'output', 'ERROR saving as HTML!!!')
            ui.queueFunction(ui.setLabelBg, 'output', 'red') 
    elif btn == "Load file":
        #load dropped or selected file and update axis listing
        ifile = ui.getEntry('file')
        ui.info('Loading file %s', ifile)
        ui.queueFunction(ui.setLabel, 'output', 'Loading file...')
        ui.queueFunction(ui.setLabelBg, 'output', 'yellow')
        try:
            df = pTS.inputFiletoDF(ifile)
            colList = df.columns
            ui.debug(colList)
            numColumns = str(len(colList))
            ui.info('Read columns from %(filename)s ---> Number of columns %(columns)s', {'filename': ifile, 'columns': numColumns})
            if numColumns == 0:
                ui.error('Loaded file has no data!!')
                ui.queueFunction(ui.setLabel, 'output', 'Loaded file has no data!!')
                ui.queueFunction(ui.setLabelBg, 'output', 'red')
            else:
                ui.clearListBox('X-Axis', callFunction=True)    
                ui.updateListBox('X-Axis', colList, select=False)
                ui.clearListBox('Y-Axis', callFunction=True)    
                ui.updateListBox('Y-Axis', colList, select=False)
                ui.clearListBox('Y2-Axis', callFunction=True)    
                ui.updateListBox('Y2-Axis', colList, select=False)
                ui.info('File loaded!')
                ui.queueFunction(ui.setLabel, 'output', 'File loaded!')
                ui.queueFunction(ui.setLabelBg, 'output', 'yellow')
        except Exception as e:
            ui.critical('%s', e)
            ui.error('Could not parse input file to dataframe!!')
            ui.queueFunction(ui.setLabel, 'output', 'ERROR loading file...')
            ui.queueFunction(ui.setLabelBg, 'output', 'red')
    elif btn == 'Load':
        #Load preset settings
        presetName = ui.getOptionBox('Preset:')
        ui.info('Loading preset %s...', presetName)
        try:
            loadPresetSettings(presetName)
        except Exception as e:
            ui.critical('%s', e)
            ui.error('Could not load settings')
    elif btn == 'Save':
        #Get preset info and save them
        presetName = ui.getOptionBox('Preset:')
        ui.info('Saving over preset %s...', presetName)
        newPresetName = ui.getEntry('Preset Name')
        ui.info('New preset name: %s', newPresetName)
        if newPresetName != '':
            changePresetValues(presetName, newPresetName)
        else:
            ui.error("Name given for preset is empty!!!")
            ui.queueFunction(ui.setLabel, 'output', 'Name given for preset is empty!!!')
            ui.queueFunction(ui.setLabelBg, 'output', 'red')
    elif btn == 'Debug':
        #activate Debug logging to file
        ui.setButton('Debug', 'Debug ON')
        ui.queueFunction(ui.setLabel, 'output', 'Debug ON')
        ui.queueFunction(ui.setLabelBg, 'output', 'yellow')
        ui.setLogFile('debug.log') #the activation by appJar function
        ui.info('plotTS %s', version)
    elif btn == 'Insert Program location -->':
        ui.setEntry('output_location', os.path.abspath(os.getcwd()), callFunction=True)
    elif btn == 'Insert Datafile location -->':
        inputfile = ui.getEntry('file')
        if inputfile != '': 
            splitted = os.path.split(inputfile)
            ui.setEntry('output_location', os.path.abspath(splitted[0]), callFunction=True)
        else:
            ui.queueFunction(ui.setLabel, 'output', 'No Datafile Loaded!...')
            ui.queueFunction(ui.setLabelBg, 'output', 'yellow')

#UI START
##General TAB and TAB start      
ui.startTabbedFrame("TabbedFrame")
ui.startTab("General")
#Data input 
ui.startFrame('Data Input', row=0, column=0, colspan=3)
ui.startLabelFrame('Drag & Drop datafile here')
ui.addLabel("dropLab", "\t\t\tDrag & Drop datafile here (or use File)\t\t\t")
ui.setLabelBg('dropLab', 'light cyan')
ui.setLabelFg('dropLab', 'grey')
try:
    ui.setLabelDropTarget("dropLab", externalDrop)
except Exception as e:
    ui.critical('%s', e)
    pass
ui.stopLabelFrame()
ui.addFileEntry("file")
ui.getEntryWidget('file').config(font="Helvetica 12")
ui.addButton('Load file', press)
ui.getButtonWidget('Load file').config(font="Helvetica 12")
ui.stopFrame()
#Axis information and data selection
ui.startFrame('Axis Frame', row=1, column=0, colspan=3)
ui.startLabelFrame('Select by clicking and use CTRL or SHIFT to add multiple items')
ui.addLabel('EmptyAxisLabel', '\t') #to remove overcrowding in the axis setting frame
ui.startFrame('X_Pane', row=1, column=0)
ui.addLabel("X_select", "Select X-Axis:")
ui.addListBox('X-Axis', '')
ui.setListBoxGroup('X-Axis', group=True)
ui.setListBoxRows('X-Axis', 14)
ui.stopFrame()
ui.startFrame('Y_Pane', row=1, column=1)
ui.addLabel("Y_select", "Select Y-Axis items:")
ui.addListBox('Y-Axis', '')
ui.setListBoxMulti('Y-Axis', multi=True)
ui.setListBoxGroup('Y-Axis', group=True)
ui.setListBoxRows('Y-Axis', 14)
ui.stopFrame()
ui.startFrame('Y2_Pane', row=1, column=2)
ui.addLabel("Y2_select", "Select Y2-Axis items:")
ui.addListBox('Y2-Axis', '')
ui.setListBoxMulti('Y2-Axis', multi=True)
ui.setListBoxGroup('Y2-Axis', group=True)
ui.setListBoxRows('Y2-Axis', 14)
ui.stopFrame()
ui.stopLabelFrame()
ui.stopFrame()
ui.stopTab() #End General Tab

#TODO add dropna parameters options (On/off, row/column, threshold..)
##Settings TAB
ui.startTab("Settings")
#Time convert settings
ui.startLabelFrame('Convert time x-axis to datetime object (strptime)')
ui.startFrame('TimeConvert_1', row=0, column=0)
ui.addRadioButton("timeconvert", "Auto")
ui.stopFrame() 
ui.startFrame('TimeConvert_2', row=0, column=1)
ui.addRadioButton("timeconvert", "Manual")
ui.stopFrame()
ui.startFrame('TimeConvert_3', row=0, column=2)
ui.addRadioButton("timeconvert", "Off")
ui.setRadioButton("timeconvert", "Off", callFunction=True)
ui.stopFrame()
ui.startFrame('TimeConvert_4', row=0, column=3, colspan=4)
ui.stretch = "column"
ui.sticky = "ew" 
ui.addLabelEntry('Time format:')
ui.setEntry('Time format:', '%Y-%m-%d %H:%M:%S%z', callFunction=True)
ui.stopFrame()
ui.startFrame('TimeConvert2_1', row=1, column=0, colspan=5)
ui.addLabel("TimeConvert_Tip", "*Tip: check python datetime library documentation on strptime format")
ui.stopFrame()
ui.stopLabelFrame()
#trace mode settings
ui.startLabelFrame('Plot trace mode') 
ui.startFrame('Trace_M_1', row=2, column=0, colspan=1)
ui.addRadioButton("trace_mode", "Lines+Markers")
ui.stopFrame()
ui.startFrame('Trace_M_2', row=2, column=1, colspan=1)
ui.addRadioButton("trace_mode", "Lines")
ui.stopFrame()
ui.startFrame('Trace_M_3', row=2, column=2, colspan=1)
ui.addRadioButton("trace_mode", "Markers")
ui.stopFrame()
ui.stopLabelFrame()
#rolling average settings
ui.startLabelFrame('Add Averaging Curves (rolling average)')
ui.startFrame('Average_1', row=3, column=0, colspan=1)
ui.addRadioButton("average", "On")
ui.stopFrame()
ui.startFrame('Average_2', row=3, column=1, colspan=1)
ui.addRadioButton("average", "Off")
ui.setRadioButton("average", "Off", callFunction=True)
ui.stopFrame()
ui.startFrame('Average_3', row=3, column=2, colspan=1)
ui.addLabel("Average_spin", "Averaging points:")
ui.stopFrame()
ui.startFrame('Average_4', row=3, column=3, colspan=1)
ui.addSpinBoxRange("average_rollNum", 1, 200)
ui.stopFrame()
ui.stopLabelFrame()
ui.startLabelFrame('Clean out empty and NaN data rows')
ui.startFrame('CleanData_1', row=4, column=0, colspan=1)
ui.addRadioButton("cleandata", "On")
ui.stopFrame()
ui.startFrame('CleanData_2', row=4, column=1, colspan=1)
ui.addRadioButton("cleandata", "Off")
ui.setRadioButton("cleandata", "Off", callFunction=True)
ui.stopFrame()
ui.startFrame('CleanData_3', row=4, column=2, colspan=2)
ui.addCheckBox("Show cleaned data rows in a pop-up")
ui.stopFrame()
ui.startFrame('CleanData_4', row=5, column=0, colspan=2)
ui.addCheckBox("Keep row if non-empty values equal to or more than:")
ui.stopFrame()
ui.startFrame('CleanData_5', row=5, column=2, colspan=1)
ui.addSpinBoxRange("cleandata_tresh", 1, 100)
ui.stopFrame()
ui.stopLabelFrame()
#empty label that squishes the settings above more together
ui.addLabel('Emptylabel', '\n\n', row=5, colspan=3, rowspan=2)
ui.stopTab() #End settings tab

##About TAB
ui.startTab("About")
ui.addLabel("Tab3_About", "plotTS uses plotly and pandas library to parse csv/xlsx files into\ndataframes and plots them with the figure shown in local browser window")
ui.addLabel('Version', 'plotTS {}'.format(version))
ui.addButton('Debug', press)
ui.setButton('Debug', 'Debug OFF')
ui.addEmptyMessage('Debug Messages')
ui.setMessageWidth('Debug Messages', 900)
ui.stopTab() #End about tab
ui.stopTabbedFrame() #END tabbing

##Bottom parts styling
ui.startFrame('Bottom', row=3, column=0, colspan=3)
ui.setBg('ghost white')

#TODO add data cleaning options
#importing presets OR creating default preset file if missing
config = ConfigParser(strict=False, interpolation=None)#interpolation none to avoid interpolation error from datetime format
presetNameValues = []
#check if exist and iterate through section names and key 'name' values
if os.path.exists('presets.ini') == True:
    config.read('presets.ini', encoding='utf-8')
    presetSectionValues = config.sections()
    ui.info('Presets loaded: %s', presetSectionValues)
    for section in config:
        presetName = config[section].get('name')
        if presetName == None: #needed to remove None value from list
            continue
        else:
            presetNameValues.append(presetName)
    ui.info('Preset names: %s', presetNameValues)
    if len(presetSectionValues) != 6:
        ui.error("ERROR presets loading failed!!!")
        ui.debug('len(presetSectionValues) = %s', str(len(presetSectionValues)))
        ui.queueFunction(ui.setLabel, 'output', 'ERROR presets loading failed!!! Possible that presets.ini corrupted!!!')
        ui.queueFunction(ui.setLabelBg, 'output', 'red')
#create new presets.ini config file as it did not exist
else:
    ui.warn('presets.ini not available')
    config['preset1'] = {
        'id': 1,
        'name': 'PresetSlotName1',
        'x_axis': '',
        'y_axis': '',
        'y2_axis': '',
        'timeconvert_mode': '',
        'timeconvert_format': '',
        'marker_trace': '',
        'avg_on': '',
        'avg_rollnum': ''
    }
    config['preset2'] = {
        'id': 2,
        'name': 'PresetSlotName2',
        'x_axis': '',
        'y_axis': '',
        'y2_axis': '',
        'timeconvert_mode': '',
        'timeconvert_format': '',
        'marker_trace': '',
        'avg_on': '',
        'avg_rollnum': ''
    }
    config['preset3'] = {
        'id': 3,
        'name': 'PresetSlotName3',
        'x_axis': '',
        'y_axis': '',
        'y2_axis': '',
        'timeconvert_mode': '',
        'timeconvert_format': '',
        'marker_trace': '',
        'avg_on': '',
        'avg_rollnum': ''
    }
    config['preset4'] = {
        'id': 4,
        'name': 'PresetSlotName4',
        'x_axis': '',
        'y_axis': '',
        'y2_axis': '',
        'timeconvert_mode': '',
        'timeconvert_format': '',
        'marker_trace': '',
        'avg_on': '',
        'avg_rollnum': ''
    }
    config['preset5'] = {
        'id': 5,
        'name': 'PresetSlotName5',
       'x_axis': '',
        'y_axis': '',
        'y2_axis': '',
        'timeconvert_mode': '',
        'timeconvert_format': '',
        'marker_trace': '',
        'avg_on': '',
        'avg_rollnum': ''
    }
    config['preset6'] = {
        'id': 6,
        'name': 'PresetSlotName6',
        'x_axis': '',
        'y_axis': '',
        'y2_axis': '',
        'timeconvert_mode': '',
        'timeconvert_format': '',
        'marker_trace': '',
        'avg_on': '',
        'avg_rollnum': ''
    }

    with open('presets.ini', 'w', encoding='utf-8') as config_file:
        config.write(config_file)
    presetSectionValues = config.sections()
    ui.info('Presets created: %s', presetSectionValues)
    #iterate through presets section names and key 'name' values
    for section in config:
        presetName = config[section].get('name')
        if presetName == None:
            continue
        else:
            presetNameValues.append(presetName)
    ui.info('Preset names: %s', presetNameValues)

#Presets part
ui.startLabelFrame('Presets')
ui.setLabelFrameBg('Presets', 'ghost white')
ui.addLabelOptionBox("Preset:", presetNameValues)
ui.startFrame('PresetButtons', row=3, column=0, colspan=1)
ui.addButtons(['Load', 'Save'], press)
ui.stopFrame()
ui.startFrame('PresetNaming', row=3, column=1, colspan=2)
ui.addLabelEntry("Preset Name")
ui.stopFrame()
ui.stopLabelFrame()

#Plot command, 
ui.addButton('Plot', press)
ui.getButtonWidget('Plot').config(font="Helvetica 12")

#SaveAsHTML directory
ui.startLabelFrame('Save as HTML save directory')
ui.startFrame('output_choise_1', row=5, column=0, colspan=1)
ui.addButton('Insert Program location -->', press)
ui.addButton('Insert Datafile location -->', press)
ui.stopFrame()
ui.startFrame('output_choise_2', row=5, column=1, colspan=3)
ui.addDirectoryEntry("output_location")
ui.stopFrame()
ui.stopLabelFrame()

#SaveAsHTML filename and button
ui.addLabelEntry('HTML filename')
ui.getLabelWidget("HTML filename").config(font="Helvetica 12")
ui.addButton('Save As HTML', press)
ui.getButtonWidget('Save As HTML').config(font="Helvetica 12")

#Output label
ui.addLabel('output')
ui.setLabel('output', "Ready - Waiting Command")
ui.setLabelBg("output", "yellow")
ui.getLabelWidget("output").config(font="Helvetica 14")

ui.stopFrame() #End bottoms part

ui.go()