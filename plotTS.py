import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import collections
import logging
import sys
from datetime import datetime
from datetime import timedelta
import re

#name the module logger
pTS_logger = logging.getLogger(__name__)
pTS_logger.setLevel(logging.DEBUG)

#convert input file to pandas dataframe
def inputFiletoDF(inputFile):
    try:
        if inputFile.endswith('.csv') == True:
            df = pd.read_csv(inputFile) #, encoding = "utf8"
        elif inputFile.endswith('.xlsx') == True:
            df = pd.read_excel(inputFile) #, encoding = "utf8"
        else:
            pTS_logger.error('Invalid file format: %s', inputFile)
        return df
    except Exception as e:
        pTS_logger.critical('%s', e)
        pTS_logger.exception('Invalid file format: %s', inputFile)

#converts given dataframes X_axis column timestamps to datetime as per datetime_format
def convertTimeValues(df, X_axis, datetime_format):
    try:
        df[X_axis] = df[X_axis].apply(lambda x: datetime.strptime(x, datetime_format))
        return df
    except Exception as e:
        pTS_logger.critical('%s', e)
        pTS_logger.exception('datetime_format is incorrect')

#converts non date timestamps to timedelta values
def convertNonDateTimeValues(timestamp):
        non24_td_list = re.split(r'(\d{1,3})(:)(\d\d)(:)?(\d\d)?(\W)?(\d{1,3})?', timestamp)
        if non24_td_list[0] == '':
            td_hours = int(non24_td_list[1])
            td_minutes = int(non24_td_list[3])
            if (non24_td_list[4] == ':') and (non24_td_list[5].isnumeric() == True):
                td_seconds = int(non24_td_list[5])
                td_milliseconds = 0
                if (non24_td_list[6] != None) and (non24_td_list[7].isnumeric() == True):
                    td_milliseconds = int(non24_td_list[7])
            else:
                td_seconds = 0
                td_milliseconds = 0
            return timedelta(hours=td_hours, minutes=td_minutes, seconds=td_seconds, milliseconds=td_milliseconds)
        else:
            raise ValueError('Timestamp regex result first group is not empty')

#automatic time conversion for given dataframe and X_axis column
def autoConvertTimeValues(df, X_axis):
    AUTO_TIME_FORMATS =[    '%Y-%m-%d %H:%M:%S',
                            '%Y-%m-%d %H:%M:%S%z',
                            '%Y-%m-%dT%H:%M:%S',
                            '%Y-%m-%dT%H:%M:%SZ',
                            '%Y-%m-%dT%H:%M:%S%z',
                            '%Y-%m-%d %H:%M',
                            '%Y/%m/%d %H:%M:%S',
                            '%Y/%m/%d %H:%M',
                            '%d/%m/%Y %H:%M:%S',
                            '%d/%m/%Y %H:%M',
                            '%Y.%m.%d %H:%M:%S',
                            '%Y.%m.%d %H:%M',
                            '%d.%m.%Y %H:%M:%S',
                            '%d.%m.%Y %H:%M',
                            '%H:%M:%S %d-%m-%Y',
                            '%H:%M %d-%m-%Y',
                            '%H:%M:%S %d/%m/%Y',
                            '%H:%M %d/%m/%Y',
                            '%H:%M:%S %d.%m.%Y',
                            '%H:%M %d.%m.%Y'
                            ]
    for format in AUTO_TIME_FORMATS:
        try:
            print(format)
            print(df[X_axis][0])
            datetime.strptime(df[X_axis][0], format)
            pTS_logger.info('Auto timestamp convert found matching format: %s', format)
            df_datetime_autoconverted = convertTimeValues(df, X_axis, format)
            return df_datetime_autoconverted
        except ValueError:
            pTS_logger.exception('time format %s is not a match', format)
            pass
    try:
        convertNonDateTimeValues(df[X_axis][0])
        df[X_axis] = df[X_axis].apply(lambda x: convertNonDateTimeValues(x))
        return df
    except Exception as e:
        pTS_logger.critical('%s', e)
        pTS_logger.exception('timestamp %s is not a match for any possible format', df[X_axis][0])
        raise ValueError('The timestamp did not match any of the allowed formats')
        
    
#add averaging data for selected items
def addAverageData(df, y_List, y2_List, average_rollNum):
    #join lists y_items and y2_items as y_joined
    try:
        y_joinedList=[]
        y_joinedList.extend(y_List)
        y_joinedList.extend(y2_List)
        pTS_logger.debug('joined y_keys for averaging: %s', y_joinedList)
        pTS_logger.debug('average rolling number %s', average_rollNum)
        df_part = df.filter(y_joinedList, axis=1)
        df_avg = df_part.rolling(average_rollNum).mean()
        for item in y_joinedList:
            df_avg = df_avg.rename(columns={item: '{}_avg={}'.format(item, average_rollNum)})
        df2 = pd.concat([df, df_avg], axis=1)
        return df2
    except Exception as e:
        pTS_logger.critical('%s', e)
        pTS_logger.exception('Issue averaging data')
    

#creates the dictionary key for plotEngine to use as figure building instructions
def createPlotDict(df, y_keys, y2_keys, trace_mode_id):
    plotDict = collections.defaultdict(dict)
    #graph line marking definitions
    if trace_mode_id == 1:
        trace_mode = 'lines+markers'
    elif trace_mode_id == 2:
        trace_mode = 'lines'
    elif trace_mode_id == 3:
        trace_mode = 'markers'

    #build keys from y_List to all primary y-axis plots
    for key in y_keys:
        plotDict[key]['name'] = key
        plotDict[key]['axis'] = 'y'
        plotDict[key]['mode'] = trace_mode
    #build keys from y2_List to all secondary y-axis plots
    for key in y2_keys:
        plotDict[key]['name'] = '{}_y2'.format(key)
        plotDict[key]['axis'] = 'y2'
        plotDict[key]['mode'] = trace_mode

    return plotDict

#plotEngine builds plots based on items in plot dictionary
def plotEngine(fig, plotDict, X_axis, df):
    #iterate through all dictionary keys
    for k in plotDict:
        #plot y-axis keys
        if plotDict[k]['axis'] == 'y':
            pName = plotDict[k]['name']
            pMode = plotDict[k]['mode']
            fig.add_trace(go.Scattergl(x=X_axis, y=df[k],
                                        mode=pMode,
                                        name=pName),secondary_y=False,)
        #plot y2-axis keys
        if plotDict[k]['axis'] == 'y2':
            pName = plotDict[k]['name']
            pMode = plotDict[k]['mode']
            fig.add_trace(go.Scattergl(x=X_axis, y=df[k],
                                        mode=pMode,
                                        name=pName),secondary_y=True,)

#TODO add dropna for given parameters
#createFig creates a figure from the data and displays the figure
def createFig(sec_y, plotDict, x_axis, df):
    #debug messages before plotting
    pTS_logger.debug('plotting dataframe...')
    pTS_logger.debug('dataframe dtypes: \n%s', df.dtypes)

    #create figure
    fig = make_subplots(specs=[[{"secondary_y": sec_y}]])

    plotEngine(fig, plotDict, x_axis, df)

    fig.show()
    pTS_logger.debug('Showing plot')

#TODO add dropna for given parameters
#saveFigAsHTML works the same as createFig, except it produces a HTML file with all the data plotted
def saveFigAsHTML(sec_y, plotDict, x_axis, df, HTML_name_path):
    #debug messages before plotting
    pTS_logger.debug('plotting dataframe...')
    pTS_logger.debug('dataframe dtypes: \n%s', df.dtypes)

    #create figure
    fig = make_subplots(specs=[[{"secondary_y": sec_y}]])

    plotEngine(fig, plotDict, x_axis, df)

    fig.write_html('{}.html'.format(HTML_name_path))
    pTS_logger.debug('Saved HTML file: %s', HTML_name_path)


#IF YOU RUN plotTS.py BY ITSELF, BELOW CODE WILL BE RUN
if __name__ == "__main__":
    #enable logging
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    #EXAMPLE DATA: starting from creating a datafile to be opened
    #creating an index to the dataframe from 0 to 99
    df_index = pd.DataFrame(np.arange(100), columns=['index'])

    #creating a time list of 100 timestamps, incrementing by 25 minutes from '2019-12-01T00:00:00'
    #also creating a list of sine values from range of 0-100
    #also creating a polynomic function of a parabola with values ranging from 0-100
    start_date = datetime.fromisoformat('2019-12-01T00:00:00')
    timelist = []
    sinelist = []
    polylist = []
    for i in range(0, 100, 1):
        timestamp = start_date + timedelta(minutes=25)*i
        timelist.append(timestamp)
        angle = (np.pi/16)*i
        sinelist.append((np.sin(angle)+1)*50)
        polyvalue = np.polyval([-0.04,4,0], i)#-0.04x^2 + 4x
        polylist.append(polyvalue)

    #putting time list to dataframe
    df_time = pd.DataFrame(data=timelist, columns=['Time'])

    #create a dataframe with 100 data point with integers ranging from 0 to 50, columns named as 'Random'
    df_random = pd.DataFrame(np.random.randint(0, 50, size=(100, 1)), columns=list(['Random']))

    #putting parabola values to dataframe
    df_poly = pd.DataFrame(data=polylist, columns=['Parabola'])

    #putting sine value list to dataframe
    df_sine = pd.DataFrame(data=sinelist, columns=['Sine'])

    #combining the time and index dataframe to the created data dataframes, creating a new dataframe named df
    df = pd.concat([df_index, df_time, df_random, df_poly, df_sine], axis=1)                                                           

    #saving the dataframe as csv                    
    df.to_csv(path_or_buf='exampledata.csv', index=False)

    #reading the input example file and generating a dataframe from it
    df_file = inputFiletoDF('exampledata.csv')

    #correcting the Time data to the imported dataframe to datetime object based on used format
    datetime_format = '%Y-%m-%d %H:%M:%S'
    df_file_with_time_corrected = convertTimeValues(df_file, 'Time', datetime_format)

    #adding rolling averagedata from 5 points to Cucumbers and Dragonfruits
    df_file_with_averages = addAverageData(df_file_with_time_corrected, ['Random'], ['Sine'], 5)

    #creating a plot Dictionary to be used in plotting
    #essentially this dictates how we want the plot to be formed
    #what items in y axis, y2 axis and what trace type
    plotDictionary = createPlotDict(df_file_with_averages, ['Parabola', 'Random', 'Random_avg=5'], [ 'Sine', 'Sine_avg=5'], 2)

    #creating the figure and plotting the data by using the 'Time' as x-axis
    createFig(True, plotDictionary, df_file_with_averages['Time'], df_file_with_averages)

    #saving the figure as html by using the 'index' as x-axis
    saveFigAsHTML(True, plotDictionary, df_file_with_averages['index'], df_file_with_averages, 'save_example')