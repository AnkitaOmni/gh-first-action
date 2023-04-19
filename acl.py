import ast
from os import system
from flask import abort


def url():
    path = r'./LogFiles/allRoutesMethods.log'
    print(path)
    system('flask routes --all-methods > ./LogFiles/allRoutesMethods.log 2>&1')
    with open(f"{path}", 'r') as logFile:
        logFileData = logFile.readlines()
    
    routePlusEndpoints = {}
    for line in logFileData[2:-2]:
        if line == "/":
            routePlusEndpoints[line.split(' ')[0].strip()] = line.split(' ')[-1].strip()
        else:
            routePlusEndpoints[line.split(' ')[0].strip()] = line.split(' ')[-1].replace('/', '').strip()    

    urls = {}
    for url in routePlusEndpoints:
        if url[0] != "_" and url[0] != "-":
            # * skip api endpoints
            urls[url] = ""
    return urls  


def is_allowed_to_read(endpoint, user_perm):
    try:
        user_perm =  ast.literal_eval(user_perm)
    except:
        abort(403)
    if 'r' in user_perm.get(endpoint, ''):
        return True
    else:
        abort(403)


def is_allowed_to_write(endpoint, user_perm):
    try:
        user_perm =  ast.literal_eval(user_perm)
    except:
        abort(403)
    if 'u' in user_perm.get(endpoint, ''):
        return True
    else:
        abort(403)


def is_allowed_to_create(endpoint, user_perm):
    try:
        user_perm =  ast.literal_eval(user_perm)
    except:
        abort(403)
    if 'c' in user_perm.get(endpoint, ''):
        return True
    else:
        abort(403)


def is_allowed_to_delete(endpoint, user_perm):
    try:
        user_perm =  ast.literal_eval(user_perm)
    except:
        abort(403)
    if 'd' in user_perm.get(endpoint, ''):
        return True
    else:
        abort(403)


if __name__ == '__main__':
    url()        
