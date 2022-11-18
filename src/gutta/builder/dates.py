from dateutil import parser
import datetime
from .exceptions import DateParsingFailure,NoDates
import numpy as np

def parse_date(datestr:str)->datetime.datetime:
    datestr = datestr.strip()
    if datestr == 'null':
        return None
    elif datestr == '':
        return None
    else:
        try:
            return parser.parse(datestr)
        except parser.ParserError:
            raise DateParsingFailure(datestr)

def daterpolation(datestrings : list[str])->list[datetime.datetime]:
    if(len(datestrings) == 0):
        return []

    dates = [ None if datestr == 'null' else parse_date(datestr) for datestr in datestrings ]
    if all(d is None for d in dates):
        raise NoDates
    
    indices = []
    tstamps = []

    for i,date in enumerate(dates):
        if date is not None:
            indices.append(i)
            tstamps.append(datetime.datetime.timestamp(date))

    interped_timestamps = np.interp(np.arange(0,len(dates)),indices,tstamps)    
    interped_dates = [datetime.datetime.fromtimestamp(ts) for ts in interped_timestamps]

    return interped_dates
