from pymongo import MongoClient
import _pickle as cPickle
from bson.binary import Binary
import numpy as np
    
def client_connect(uri = 'mongodb://localhost:27017', returnList = False):
    '''
    Connects to local mongodb client at localhost port 27017 or URI of your atlas cluster and returns list of databases
    
    Parameters:
        uri (str): URI of mongodb instance if available, otherwise default local mongod instance
        returnList(bool): returns list of databases if you don't know what's available
        
    Returns:
        pymongo.mongo_client.MongoClient and list of database names if wanted
    '''
    client = MongoClient(uri)
    dbList = []
    for db in client.list_databases():
        dbList.append(db)
    dbList = [x['name'] for x in dbList]
    if returnList == False:
        return client
    else:
        return client, dbList

def database_connect(client, database, returnList = False):
    '''
    Connects to database
    
    Parameters:
        client(pymongo.mongo_client.MongoClient): client object
        database(str): name of database 
        returnList(bool): returns list of collections if you don't know what's available
        
    Returns:
        pymongo.database.Database and list of collection names if wanted
    '''
    database = getattr(client, database)
    colList = []
    for col in database.list_collections():
        colList.append(col['name'])
    if returnList == False:
        return database
    else:
        return database, colList

def convert_ndarray_binary(data):
    '''
    Converts ndarray into a mongo saveable format
    
    Paramters:
        data(ndarray): numpy array to convert
        
    Returns:
        mongo/json saveable format for data
    '''
    return Binary(cPickle.dumps(data, protocol = 2))
    
def convert_binary_ndarray(data):
    '''
    Converts the binary data into an ndarray
    
    Parameters:
        data (bytes): input data
        
    Returns:
        ndarray 
    '''
    return np.asarray(cPickle.loads(data))