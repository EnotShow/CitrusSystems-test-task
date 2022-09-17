from bson import ObjectId
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import USERS, TRANSACTIONS, GAMES
from api.serializers import TransactionsSerializer, GameBuySerializer, GameCreateSerializer, RefillSerializer
from api.utils import api_auth_check, make_transaction
from config.settings import DATABASE


@api_view(['POST'])
@api_auth_check
def refund(request):
    """ Transaction rollback api """
    try:
        deposit_id = request.POST['deposit_id']
        serializer = TransactionsSerializer(data=[{'deposit_id': deposit_id}], many=True)
        if not serializer.is_valid:
            raise ValueError
        deposit = TRANSACTIONS.find_one(ObjectId(deposit_id))
        if deposit['status'] in ['refunded', 'failed']:
            raise ValueError
        if deposit['action'] == 'increment':
            amount = -int(deposit['value'])
        elif deposit['action'] == 'decrement':
            amount = int(deposit['value'])

        new_value = {'$inc': {'balance': amount}}
        user_filter = {'username': deposit['username']}

        USERS.update_one(user_filter, new_value)
        new_value = USERS.find_one({'username': deposit['username']})['balance']

        TRANSACTIONS.update_one({'_id': ObjectId(deposit_id)}, {'$set': {'status': 'refunded'}})
        return Response({'status': 'ok', 'balance': new_value, 'message': 'success'})
    except Exception:
        return Response({'status': 'failed', 'message': 'error'})


@api_view(['POST'])
@api_auth_check
def buy_game(request):
    """ Buy game api """
    try:
        game_id = request.POST['game_id']
        username = request.POST['username']
        serializer = GameBuySerializer(data=[{'game_id': game_id}], many=True)
        if not serializer.is_valid:
            raise ValueError

        user = USERS.find_one({'username': username})
        game = GAMES.find_one({'_id': ObjectId(game_id)})

        if not game:
            return Response({'status': 'failed', 'message': 'unknown'})

        if int(user['balance']) > int(game['price']):
            amount = int(game['price'])
            make_transaction(username=username, amount=amount, increment=False)
            new_balance = USERS.find_one({'username': username})['balance']
            return Response({
                'status': 'ok',
                'game_id': str(game['_id']),
                'balance': new_balance,
                'message': 'success'
            })

        else:
            return Response({'status': 'failed', 'message': 'insufficient_funds'})
    except Exception:
        return Response({'status': 'failed', 'message': 'error'})


@api_view(['POST'])
@api_auth_check
def create_game(request):
    """ Game creation api """
    try:
        name = request.POST['name']
        title = request.POST['title']
        price = request.POST['price']
        serializer = GameCreateSerializer(data=[{'name': name, 'title': title, 'price': price}], many=True)
        if not serializer.is_valid:
            raise ValueError

        find = GAMES.find_one({'name': name})
        if find:
            raise ValueError
            # return Response({'status': 'failed', 'message': 'duplicate'})

        game = GAMES.insert_one({'name': name, 'title': title, 'price': price})
        return Response({'status': 'ok', 'game_id': str(game.inserted_id), 'message': 'success'})
    except Exception:
        return Response({'status': 'failed', 'message': 'error'})


@api_view(['POST'])
@api_auth_check
def refill(request):
    """ Refilling api """
    try:
        username = request.POST['username']
        amount = int(request.POST['amount'])
        serializer = RefillSerializer(data=[{'username': username, 'amount': amount}], many=True)
        if not serializer.is_valid:
            raise ValueError

        transaction_id = make_transaction(username=username, amount=amount, increment=True)
        new_balance = USERS.find_one({'username': username})['balance']
        return Response({
            'status': 'ok',
            'deposit_id': str(transaction_id),
            'balance': new_balance,
            'message': 'success'
        })
    except Exception:
        return Response({'status': 'failed', 'message': 'error'})
