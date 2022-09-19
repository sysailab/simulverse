
def resolve_error(error:str):
    if error == '401':
        return 'HTTP 401 UNAUTHORIZED'
    if error == '10':
        return "I don't know"