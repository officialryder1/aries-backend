# django util
from django.http import JsonResponse  # noqa: F401
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.db.models import Q
from django.views.decorators.http import require_POST

# third parties
from .pusher import pusher_client
# models
from ..models import Note, Character, Player, Player_rank, Card, Rarity, Match, MatchResult, PlayerCard, MatchRequest  # noqa: F401
from .serializers import UserSerializer, RegisterSerializer, NoteSerializer, CardSerializer, CharacterSerializer, PlayerSerializer, MatchSerializer, MatchResultSerializer, PlayerCardSerializer, MatchRequestSerializer

# restFrameWork 
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.http import require_GET


@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/token: POST',
        '/api/token/refresh: POST',
        '/api/register: POST',
        '/api/notes: GET',
        '/api/create_note: POST',
        '/api/user/${int}: GET',
        '/api/delete/${int}: DELETE',
        'api/cards: POST, GET',
        'api/characters:GET',
        'api/create_avatar: POST',
        'api/get_player: GET',
        'api/get_card/<int:pk>: GET',
        'api/update_player: POST',
        'api/get_character/{params}: GET',
        'api/game/match: GET',
        'api/game/match_request: POST, GET',
        'api/game/find_match: POST',
        'api/game/accept_match/{params}: GET',
        'api/game/match/{params}: GET',
        'api/game/matchDetail: GET',
        'api/game/match_status/: GET',
        'api/game/pending_matches/: GET',
        'api/trigger_card: POST',
        'api/match_result: GET'
    ]
    return Response(routes)

    

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        # ...

        return token
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer



@require_GET
def check_user_exists(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'User ID is required'}, status=400)

    try:
        user = User.objects.get(pk=user_id)
        return JsonResponse({'exists': True})
    except User.DoesNotExist:
        return JsonResponse({'exists': False})
    

@api_view(['GET'])
def getUser(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getNote(request):
    user = request.user
    notes = user.note_set.all()
    serializer = NoteSerializer(notes, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_note(request):
    serializer = NoteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT', 'DELETE'])
def delete_note(request, pk):
    try:
        note = Note.objects.get(pk=pk)
    except Note.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    note.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def create_avatar(request):
    serializer = PlayerSerializer(data=request.data)
    # user = request.user
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET'])
def character(request):
    if request.method == 'GET':
        character = Character.objects.all()
        serializer = CharacterSerializer(character, many=True)
        return Response(serializer.data)

# get all the cards and listen for a post event to add card
@api_view(['POST', 'GET'])
def card(request):
    if request.method == 'GET':
        card = Card.objects.all()
        serializer = CardSerializer(card, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer = CardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


@api_view(['GET'])
def get_player(request):
    user_id = request.GET.get('user_id')  # Use 'user_id' to get the user ID from query parameters

    if not user_id:
        return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(pk=user_id)  # Fetch the user object by ID
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    players = Player.objects.filter(user=user)  # Filter players by the user
    serializer = PlayerSerializer(players, many=True)


    return Response(serializer.data, status=status.HTTP_200_OK)


# Get a single card 
@api_view(['GET'])
def get_card(request, pk ):
    try:
        card = Card.objects.get(pk=pk)
        serializer = CardSerializer(card)
        
        return Response(serializer.data)
    except Card.DoesNotExist:
        return Response({'error': "Card not found"}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def update_player_card(request):
    user = request.GET.get('user_id')
    try:
        player = Player.objects.get(user=user)
    except Player.DoesNotExist:
        return Response({"error": "Player not found"}, status=status.HTTP_404_NOT_FOUND)
    
    cards = request.data.get('card', [])
    if not cards:
        return Response({"error": "No cards provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    card_objects = Card.objects.filter(id__in=cards)
    player.card.set(card_objects)
    player.save()

    serializer = PlayerSerializer(player)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_character(request, pk):
    try:
        character = Character.objects.get(pk=pk)
        serializer = CharacterSerializer(character)
        return Response(serializer.data)
    except Character.DoesNotExist:
        return Response({"error": "Character not found"}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', 'POST'])
def match(request):
    if request.method == 'GET':
        match = Match.objects.all()
        serializer = MatchSerializer(match, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        pass

@api_view(['GET', 'POST'])
def requestMatch(request):
    user = request.GET.get('user_id')
    user_id = User.objects.get(pk=user)
    match_request = MatchRequest.objects.create(requester=user_id)

    match_request.save()
    pusher_client.trigger('match-channel', 'new-match', {
        'requester_name': match_request.requester.username,
        'match_request_id': match_request.id
    })
    return Response({"message": "Searching for a match..."})

@api_view(['POST', 'GET'])
def FindMatch(request):
    user = request.GET.get('user_id')

    
    match_request = MatchRequest.objects.filter(status='pending').exclude(requestee=user)
    serializer = MatchRequestSerializer(match_request, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def AcceptMatch(request, pk):    
        user_id = request.GET.get('user_id')

        # Validate and retrieve the player
        try:
            player = Player.objects.get(user=user_id)
        except Player.DoesNotExist:
            return Response({"error": "Player not found"}, status=status.HTTP_404_NOT_FOUND)
        
        #Match event creation
    
        try:
            match_request = MatchRequest.objects.get(pk=pk, status="pending")
        except MatchRequest.DoesNotExist:
            return Response({"error": "Match request not found or already accepted"}, status=status.HTTP_404_NOT_FOUND)
        
        match_request.requestee = player.user
        match_request.status = "accepted"
        match_request.save()

        match = Match.objects.create(player_one=match_request.requester, player_two=player.user)

        pusher_client.trigger('match-channel', 'match-accepted', {
            'message': f'User {user_id} has accepted the match!',
            'match_id': match.id,
            'redirect_url': f'/game/{match.id}',
            'player_one_id': match.player_one.id,
            'player_two_id': match.player_two.id,
        })
        # Create the match instance
        match_url = reverse('matchDetail', kwargs={'pk': match.id})
       
        return Response({"message": "Match accepted", "redirect_url": match_url}, status=status.HTTP_200_OK)
       
@api_view(['GET'])
def matchDetail(request, pk):
    match = get_object_or_404(Match, pk=pk)
    
    serializer = MatchSerializer(match)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def match_status(request):
    user_id = request.GET.get('user_id')

    # Validate and retrieve the player
    try:
        player = Player.objects.get(user=user_id)
    except Player.DoesNotExist:
        return Response({"error": "Player not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Retrieve the match where the player is involved
    match = Match.objects.filter(player_one=player.user).first() or Match.objects.filter(player_two=player.user).first()

    if not match:
        return Response({"status": "No match found"}, status=status.HTTP_200_OK)

    # Serialize the match details
    serializer = MatchSerializer(match)
    return Response({"status": match.status, "match": serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
def pending_matches(request):
    user_id = request.GET.get('user_id')

    # Validate and retrieve the player
    try:
        player = Player.objects.get(user=user_id)
    except Player.DoesNotExist:
        return Response({"error": "Player not found"}, status=status.HTTP_404_NOT_FOUND)

    # Find all pending matches for this player
    pending_matches = Match.objects.filter(
        (Q(player_one=player.user) | Q(player_two=player.user)),
        status="waiting"
    )

    if not pending_matches.exists():
        return Response({"status": "No pending matches found"}, status=status.HTTP_200_OK)

    # Serialize the pending matches
    serializer = MatchSerializer(pending_matches, many=True)
    return Response({"pending_matches": serializer.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
def trigger_card_event(request):
    card_id = request.data.get('card')
    username = request.data.get('user')
    match_id = request.data.get('match')

    match = get_object_or_404(Match, id=match_id)
    player_one = match.player_one
    player_two = match.player_two

    player_one_detail = get_object_or_404(Player, user=player_one)
    player_two_detail = get_object_or_404(Player, user=player_two)

    card = get_object_or_404(Card, id=card_id)
    serializer = CardSerializer(card)
    player_attack = card.attack_point
    card_mana = card.mana_point

    if username == player_one.username:
        opponent = player_two_detail
        player = player_one_detail
    elif username == player_two.username:
        opponent = player_one_detail
        player = player_two_detail
    else:
        return Response({'status': 'error', 'message': 'Invalid user'}, status=400)

    if player.hp > 0:
        if player.mana >= card_mana:
            if opponent.hp > 0:
                opponent.hp -= player_attack
                player.mana -= card_mana
                opponent.save()
                player.save()

                # Real-time update via Pusher
                pusher_client.trigger('match-channel', 'get-card', {
                    'card': serializer.data,
                    'user': username,
                    'player_one_health': player_one_detail.hp,
                    'player_two_health': player_two_detail.hp,
                    'player_one_mana': player_one_detail.mana,
                    'player_two_mana': player_two_detail.mana
                })

                if opponent.hp <= 0:
                    winner = player.user
                    loser = opponent.user
                    match_result = MatchResult.objects.create(match=match, winner=winner, loser=loser)
                    match_result.winning_cards.set([card])
                    match_result.save()
                    return Response({'message': 'You won the match', 'winner': winner.username})
            else:
                return Response({'message': 'Opponent has already been defeated'})
        else:
            return Response({'message': 'Out of mana'})
    else:
        return Response({'message': 'You have been defeated'})

    return Response({'status': 'success'})

@api_view(['POST', 'GET'])
def match_result(request):
    user = request.data.get('user')
    match_id = request.data.get('match')

    match = get_object_or_404(Match, id=match_id)
    match_result = get_object_or_404(MatchResult, match=match)
    
    # * retrieve match details
    winner = match_result.winner
    loser = match_result.loser
    winning_card = match_result.winning_cards.all()

    # Logic for claiming loser card
    player = get_object_or_404(Player, user=loser)
    loser_cards = player.card.all()

    card_serializer = CardSerializer(loser_cards, many=True)
  

    # Serialize the winner, loser, and winning cards
    winner_serializer = UserSerializer(winner)
    loser_serializer = UserSerializer(loser)
    winning_card_serializer = CardSerializer(winning_card, many=True)

    # Compare the username provided in the request with the winner's username
    if user == winner.username:
        message = "You won the match"
    else:
        player.hp = 100
        player.mana = 100
        player.save()
        message = " You lost the match"

    return Response({
            'message': message, 
            'winner': winner_serializer.data, 
            'loser': loser_serializer.data, 
            'winning_card': winning_card_serializer.data,
            'loser_card': card_serializer.data
        })

@api_view(['POST'])
def pick_loser_card(request, match_id):
    card_id = request.data.get('card_id')
    match = get_object_or_404(Match, id=match_id)
    match_result = get_object_or_404(MatchResult, match=match)
    winner = match_result.winner

    loser_player = get_object_or_404(Player, user=match_result.loser)
    winner_player = get_object_or_404(Player, user=winner)

    # Transfer card to teh winner
    card = get_object_or_404(Card, id=card_id)
   
    loser_player.card.remove(card)
    winner_player.card.add(card)
    winner_player.mana += card.mana_point
    winner_player.hp += card.attack_point
    winner_player.save()

    return Response({'message': 'Card successfully transferred to winner'})

@api_view(['GET'])
def get_player_rank(request):
    user = request.GET.get('user')


    player = get_object_or_404(Player, user=user)
    player_cards = player.card.all()
    
   # Initialize total points
    total_cards_points = 0
    rank = ''
    time_interval = 0

    # Loop through each card to sum the points
    for card in player_cards:
        total_cards_points += card.card_point or 0
        # total_mana_points += card.mana_point or 0
        if total_cards_points <= 500:
            rank = 'D'
            time_interval = 15
        elif total_cards_points <= 500 and total_cards_points < 200:
            rank = 'C'
            time_interval = 11
        elif total_cards_points <= 700 and total_cards_points > 500:
            rank = 'B'
            time_interval = 9
        elif total_cards_points <=1500 and total_cards_points > 700:
            rank = 'A'
            time_interval = 7
        elif total_cards_points > 1500:
            rank = 'S'
            time_interval = 5

    # Return the total points along with the rank or any other info you need
    return Response({
        'user': user,
        'total_attack_points': total_cards_points,
        'rank': rank,
        'time_interval': time_interval
       
    })

