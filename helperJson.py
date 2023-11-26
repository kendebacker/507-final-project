import json

# Code from https://docs.google.com/presentation/d/1BHPzpBnZOtTwObtQpA1rzynxYgsWxvUXG98QSu3v0Z8/edit#slide=id.gf5d8039965_1_13
def fetchCache(filepath):
    ''' gets saved data
    
    Parameters
    ----------
    filepath:  str
        filepath

    Returns
    -------
    dictionary of stored data
    '''

    file = open(filepath, 'r')
    fileContents = file.read()
    data = json.loads(fileContents)
    file.close()
    return data
