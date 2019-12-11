import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import collections
import logging

#name the module logger
pTS_logger = logging.getLogger(__name__)

#convert input file to pandas dataframe
def inputFiletoDF(inputFile):
    if inputFile.endswith('.csv') == True:
        df = pd.read_csv(inputFile) #, encoding = "utf8"
    elif inputFile.endswith('.xlsx') == True:
        df = pd.read_excel(inputFile) #, encoding = "utf8"
    else:
        pTS_logger.error('Invalid file format')

    return df

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

#createFig creates a figure from the data and displays the figure
def createFig(sec_y, plotDict, x_axis, df):
    #create figure
    fig = make_subplots(specs=[[{"secondary_y": sec_y}]])

    plotEngine(fig, plotDict, x_axis, df)

    fig.show()

#saveFigAsHTML works the same as createFig, except it produces a HTML file with all the data plotted
def saveFigAsHTML(sec_y, plotDict, x_axis, df, HTML_name):
    #create figure
    fig = make_subplots(specs=[[{"secondary_y": sec_y}]])

    plotEngine(fig, plotDict, x_axis, df)

    fig.write_html('{}.html'.format(HTML_name))

if __name__ == "__main__":
    #TODO create example for the release version
    print('Example missing :(')
