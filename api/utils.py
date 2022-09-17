from functools import wraps

from bson import ObjectId
from rest_framework.response import Response

from api.models import SESSIONS, TRANSACTIONS, USERS


def api_auth_check(view_func):
    """ Return func if user is authenticated """
    @wraps(view_func)
    def decorator_func(request, *args, **kwargs):
        try:
            token = request.headers['Token']
        except KeyError:
            return Response({'status': 'failed', 'message': 'unauthorized'})
        find_token = SESSIONS.find_one({'token': token})['token']
        if token == find_token:
            return view_func(request, *args, **kwargs)
        else:
            return Response({'status': 'failed', 'message': 'unauthorized'})
    return decorator_func


def make_transaction(username: str, amount: int, increment: bool) -> ObjectId:
    """ Func that made a transaction """
    transaction = TRANSACTIONS.insert_one({
        'username': username,
        'value': amount,
        'action': 'increment' if increment else 'decrement',
        'status': 'processed'
    })
    find_filter = {'username': username}
    new_value = {'$inc': {'balance': amount if increment else -amount}}
    try:
        USERS.update_one(find_filter, new_value)
    except Exception:
        TRANSACTIONS.update_one({'_id': transaction.inserted_id}, {'$set': {'status': 'failed'}})
    else:
        TRANSACTIONS.update_one({'_id': transaction.inserted_id}, {'$set': {'status': 'complete'}})
    return transaction.inserted_id
