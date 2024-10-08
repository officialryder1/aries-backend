
from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Note, Player, Card, Character, Rarity, Player_rank, MatchResult, Match, PlayerCard, MatchRequest

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    
class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'

class PlayerSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    character_name = serializers.SerializerMethodField()
    card = serializers.PrimaryKeyRelatedField(queryset=Card.objects.all(), many=True, required=False)

    class Meta:
        model = Player
        fields = ['user', 'user_name', 'character', 'character_name', 'card', 'hp', 'mana']

    def get_user_name(self, obj):
        return obj.user.username
    
    def get_character_name(self, obj):
        return obj.character.name
    
class MatchRequestSerializer(serializers.ModelSerializer):
    requester_name = serializers.SerializerMethodField()
    class Meta:
        model = MatchRequest
        fields = ['id','status', 'created_at', 'requestee', 'requester', 'requester_name']

    def get_requester_name(self, obj):
        return obj.requester.username

class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = '__all__'

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'

class RaritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Rarity
        fields = '__all__'

class PlayerRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player_rank
        fields = '__all__'

class MatchSerializer(serializers.ModelSerializer):
    playerone = serializers.SerializerMethodField()
    playertwo = serializers.SerializerMethodField()
    
    class Meta:
        model = Match
        fields = ['id','player_one','playerone', 'player_two', 'playertwo', 'status', 'end_time', 'winner']

    def get_playerone(self, obj):
        return obj.player_one.username

    def get_playertwo(self, obj):
        return obj.player_two.username

class MatchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchResult
        fields = '__all__'

class PlayerCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerCard
        fields = '__all__'

