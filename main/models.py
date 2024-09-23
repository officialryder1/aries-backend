from django.db import models
from django.contrib.auth.models import User


class  Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    
    def __str__(self):
        return str(self.user)


class Character(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="characters")
    second_image = models.ImageField(upload_to="character_second", blank=True, null=True)

    def __str__(self):
        return self.name

class Rarity(models.Model):
    rank = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.rank

class Card(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='Card')

    card_point = models.PositiveIntegerField(default=0)
    card_type = models.ForeignKey(Character, on_delete=models.CASCADE)
    attack_point = models.PositiveIntegerField(default=0)
    defense_point = models.PositiveIntegerField(default=0)
    can_nullify = models.BooleanField(default=False, blank= True, null=True)

    rarity = models.ForeignKey(Rarity, on_delete=models.CASCADE)
    mana_point = models.PositiveIntegerField(default = 0, blank=True, null=True)

    def __str__(self):
        return self.name
    

class Player_rank(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rarity = models.ForeignKey(Rarity, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)

class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    card = models.ManyToManyField(Card, related_name='player_cards', blank=True)

    hp = models.IntegerField(default=100)
    mana = models.IntegerField(default=100)

    def __str__(self):
        return str(self.user)


# Match db

class Match(models.Model):
    player_one = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_one')
    player_two = models.ForeignKey(User, on_delete=models.CASCADE, related_name="player_two")
    status = models.CharField(max_length=20, choices=[(
        'waiting', 'Waiting'), ('ongoing', 'Ongoing'), ('finished', 'Finished')], default= 'waiting')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='match_won')

    def __str__(self):
        return f"Match between {self.player_one.username} and {self.player_two.username}"



class PlayerCard(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_cards')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="player_card")
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="player_card")
    in_hand = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.player.username}'s {self.card.name} in match {self.match.id}"
    
class MatchResult(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name="result")
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="won_match")
    loser = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "lost_match")
    winning_cards = models.ManyToManyField(Card, related_name='winning_matches')

    def __str__(self):
        return f"Result of match {self.match.id}"
    

class MatchRequest(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requested_matches")
    requestee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recieved_matches", null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')], default ="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request was created by {self.requester} on {self.created_at}"
    