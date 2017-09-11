from django.utils import timezone
from django.test import TestCase
import random

import string

from mafiaapp.models import Game,User

def randomcode():
    return ''.join(random.choice(string.lowercase) for i in range(5))


class GameModelTests(TestCase):
    code1 = randomcode()
    code2 = randomcode()

    def setUp(self):
        Game.objects.create(game_code=self.code1)
        Game.objects.create(game_code=self.code2)

    def testGameCreation(self):
        first = Game.objects.get(game_code=self.code1)
        second = Game.objects.get(game_code=self.code2)
        self.assertEqual(first.game_code, self.code1)
        self.assertEqual(second.game_code, self.code2)
        first.delete()
        second.delete()

class UserModelTests(TestCase):
    name1 = 'tim'
    name2 = 'bob'
    def setUp(self):
        User.objects.create(role=1, name=self.name1, creator=True)
        User.objects.create(name=self.name2)

    def testUserCreation(self):
        first = User.objects.get(name=self.name1)
        second = User.objects.get(name=self.name2)
        self.assertEqual(first.name, self.name1)
        self.assertEqual(second.role, 0) #default should be 0
        first.delete()
        second.delete()


