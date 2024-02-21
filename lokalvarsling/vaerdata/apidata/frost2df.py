
""" Get pandas DataFrames from the frost.met.no API



This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.

__author__ = "Ketil Tunheim"
__contact__ = "ketilt@met.no"
__date__ = "2020/02/07"
__license__ = "GPLv3"
__version__ = "0.0.1"

"""

import io
import requests
import pandas as pd

# for 414 (url) tackling
#from itertools import islice

# Input your own client ID
client_id = 'b8b1793b-27ff-4f4d-a081-fcbcc5065b53'
client_secret = '7f24c0ca-ca82-4ed6-afcd-23e657c2e78c'

# Only endpoint is a mandatory argument
# endpoint - piece of frost.met.no URI, e.g. 'observations/availableTimeSeries'
# parameters - dictionary with keys corresponding to fields in the API Reference of frost.met.no
# outformat - csv available for observations, ualf required for lightning
# version - v0 available, v1 under development
# verbose - will output URIs and extra metadata
# RETURNS pandas DataFrame
def frost2df(endpoint, parameters={}, outformat='jsonld', version='v0', verbose=False):
    # Build the Frost URL and get data from the API
    endpoint_url = 'https://frost.met.no/{endpoint}/{version}.{format}'.format(
        endpoint=endpoint,
        version=version,
        format=outformat
    )
    r = requests.get(endpoint_url, parameters, auth=(client_id,client_secret))
    if verbose:
        print(r.url)

    # If errors, print them and output and empty dataframe
    if r.status_code != 200:
        print('Error! Returned status code %s' % r.status_code)
        error = r.json()['error']
        for part in ['message','reason','help']:
            if part in error:
                print(part.upper(), ': ', error[part])

        return pd.DataFrame()

    # Accept jsonld, csv or ualf formats when possible
    if outformat == 'jsonld':
        data = r.json()['data']
    elif outformat == 'csv':
        data = r.content
        return pd.read_csv(io.StringIO(data.decode('utf-8')))
    elif outformat == 'ualf':
        data = r.content.decode('utf-8')
        if len(data) == 0:
            print('No lightning data found for these parameters.')
            return pd.DataFrame()
        else:
            return pd.read_csv(io.StringIO(data),sep=' ',header=0)

    # Consider the unique JSON structures in some of the endpoints
    if endpoint == 'observations':
        return pd.json_normalize(data,record_path=['observations'],meta=['sourceId','referenceTime'])
    elif endpoint == 'frequencies/rainfall':
        return pd.json_normalize(data,record_path=['values'],meta=['sourceId'])
    elif endpoint == 'elements/codeTables':
        if verbose:
            print(data[0]['description'])
            print(data[0]['additionalInfo'])
            print('%s elements' % data[0]['size'])
        return pd.json_normalize(data,record_path=['values'])
    elif endpoint == 'observations/availableQualityCodes':
        return pd.json_normalize(data,record_path=['summarized'])
    elif endpoint == 'observations/quality':
        if 'fields' not in parameters and verbose:
            print('Description of flag %s:' % data['flag'])
            print('Quality code %s (%s)' % (data['summarized']['value'], data['summarized']['shortMeaning']))
            print(data['summarized']['meaning'])
        if 'fields' not in parameters or parameters['fields'] == 'details':
            return pd.json_normalize(data,record_path=['details'])
        else:
            return pd.json_normalize(data)
    else:
        return pd.json_normalize(data)


# Wrapper for the lightning endpoint
# parameters - dict with referencetime, maxage and geometry
#    Examples:
#        'geometry': 'POINT(10.933 50.345)'
#        'geometry': 'nearest(POINT(10.933 50.345))'
#        'geometry': 'POLYGON((10 59, 10 60, 11 60, 11 59, 10 59))'
# defines column headers
def lightning2df(parameters, verbose=False):
    df = frost2df('lightning', parameters, outformat='ualf', verbose=verbose)
    if len(df) > 0:
        df.columns = [
            'versionNumber','year','month','day','hour',
            'minute','second','nanosecond','width','length',
            'peakCurrent(kA)','multiplicityForFlashData','numberOfSensors',
            'degreesOfFreedom','ellipseAngle','lengthofSemiMajorAxis','lengthofSemiMinorAxis',
            'chiSquareValue','risetimeOfWaveform(ms)','peakToZeroTime','maxRateOfRise',
            'cloudIndicator','angleIndicator','signalIndicator','timingIndicator'
        ]

    return df

# Wrapper for the observations endpoint. Parameters in order:
#   sources (string)
#   elements (string)
#   referencetime (string)
#   parameters (dict)
# All of these will default to false if not given.
# Error if insufficient information entered.
# The three first parameters will suoercede what is given in fourth argument,
# but otherwise they will be combined.
def obs2df(sources=False, elements=False, referencetime=False, parameters=False, verbose=False):
    df = obsprep(sources, elements, referencetime, parameters, verbose)
    if len(df) > 0:
        cols = ['sourceId','elementId','referenceTime','value']
        more_cols = ['unit','qualityCode','timeOffset','timeResolution', 'level.value']
        for col in more_cols:
            if col in df.columns:
                cols.extend([col])

        df = df[cols]

    return df

# Wrapper for the observations endpoint. Only two columns. Parameters in order:
#   sources (string)
#   elements (string)
#   referencetime (string)
#   parameters (dict)
# All of these will default to false if not given.
# Error if insufficient information entered.
# The three first parameters will suoercede what is given in fourth argument,
# but otherwise they will be combined.
def obsthin(sources=False, elements=False, referencetime=False, parameters=False, verbose=False):
    df = obs2df(sources, elements, referencetime, parameters, verbose)
    df['referenceTime'] = df['referenceTime'].dt.strftime('%Y-%m-%d %H:%M')
    return df[['referenceTime','value']]

# Plot using the in-built matplotlib functionality in pandas
#   sources (string)
#   elements (string)
#   referencetime (string)
#   parameters (dict)
# All of these will default to false if not given.
# Error if insufficient information entered.
# The three first parameters will suoercede what is given in fourth argument,
# but otherwise they will be combined.
def plotobs(sources=False, elements=False, referencetime=False, parameters=False, verbose=False):
    df = obsprep(sources, elements, referencetime, parameters, verbose)
    if len(df) > 0:
        keys = ['sourceId','elementId','timeResolution','timeOffset','timeSeriesId']
        if 'level.value' in df:
            df['level'] = df['level.value']
            keys.extend(['level'])

        piv = df.pivot_table(index='referenceTime', columns=keys, values='value')
        # removing TZ info only to suppress pandas warning
        piv.index = piv.index.tz_localize(None)
        piv.plot()


# Choose a station based on a name search
#   name - case-insensitive name, wildcard will be used on both ends
def stnr(names):
    sourceids = []
    if type(names) is str:
        names = [names]

    for name in names:
        wname = '*%s*' % name
        df = frost2df('sources', parameters={'name': wname})
        if len(df) > 0:
            sourceid = df['id'].values[0]
            if len(df) > 1:
                df['both'] = df.apply(lambda x: '%s %s' % (x['id'], x['name']), axis=1)
                choice = '%s %s' % (sourceid, df['name'].values[0])
                print('Found following stations and chose %s:' % choice)
                print(df['both'].str.cat(sep='\n'))

            sourceids.extend([sourceid])

    return ",".join(sourceids)

# Wrapper for getting a code table
#   tablename - the id of the code table
#   element_id - the element_id to show a code table for
#   oldcode - the old element code to show a code table for
#   lang - en-US, nb-NO (default), nn-NO
def codetable(tablename=False, element_id=False, oldcode=False, lang='nb-NO'):
    # tablename is easiest, otherwise prepare parameters
    if tablename is not False:
        return frost2df('elements/codeTables', {'ids':tablename,'lang':lang}, verbose=True)
    elif element_id is not False:
        params = {'ids': element_id}
    elif oldcode is not False:
        params = {'oldElementCodes': oldcode}
    else:
        print('Insufficient information')
        return pd.DataFrame()
    # request from elements to find tablename
    element = frost2df('elements', params, verbose=True)
    print('') # extra newline
    # what was returned?
    if len(element) == 0:
        print('No matches for element ID')
        return pd.DataFrame()        
    elif len(element) > 1:
        print('Multiple matches for element ID, choosing %s' % element['id'][0])
    if 'codeTable' not in element:
        print('Element does not have a code table')
        return pd.DataFrame()
    # get tablename and fetch this table
    tablename = element['codeTable']
    return frost2df('elements/codeTables', {'ids':tablename,'lang':lang}, verbose=True)


# Helping function - get tables of available parameters and responses!
#   endpoint - the name of the endpoint (ex. observations)
def help(endpoint):
    # get swagger json
    swagger = 'https://frost.met.no/swagger.json'
    r = requests.get(swagger, {}, auth=(client_id,client_secret))
    paths = r.json()['paths']

    # get endpoint info is possible
    endpoint_sw = '/%s/v0.{format}' % endpoint
    if endpoint_sw not in paths:
        print('Endpoint %s not found' % endpoint)
        return False
    endpoint_js = paths[endpoint_sw]['get']

    # print info and return table
    print(endpoint_js['summary'])
    print(endpoint_js['description'])

    params = endpoint_js['parameters']
    df_params = pd.json_normalize(params).set_index('name')

    responses = endpoint_js['responses']
    df_responses = pd.json_normalize(responses).T
    df_responses = df_responses[~df_responses.index.str.contains('schema')]
    df_responses.index = df_responses.index.map(lambda x: x[0:3])
    df_responses.columns = ['status code description']

    return df_params, df_responses


# Unexported helping function for obs wrappers
def obsprep(sources=False, elements=False, referencetime=False, parameters=False, verbose=False):
    if parameters is False:
        parameters = {}

    if sources is not False and elements is not False and referencetime is not False:
        parameters['sources'] = sources
        parameters['elements'] = elements,
        parameters['referencetime'] = referencetime

    if parameters is False:
        print('Either parameters must be defined, or sources, elements and referencetime must all be defined.')

    df = frost2df('observations', parameters, verbose=verbose)
    if len(df) > 0:
        df['referenceTime'] = pd.to_datetime(df['referenceTime'])

    return df