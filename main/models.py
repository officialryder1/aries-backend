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

    rarity = models.ForeignKey(Rarity, on_delete=models.CASCADE)
    mana_point = models.PositiveIntegerField(blank=True, null=True)

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

    hp = models.PositiveIntegerField(default=100)
    mana = models.PositiveIntegerField(default=100)

    def __str__(self):
        return str(self.user)




