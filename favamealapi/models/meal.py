from django.db import models
from django.contrib.auth.models import User

class Meal(models.Model):
    """Meal Model
    """
    name = models.CharField(max_length=55)
    restaurant = models.ForeignKey("Restaurant", on_delete=models.CASCADE)
    favorites= models.ManyToManyField(User, through='FavoriteMeal',related_name='meals')
    ratings = models.ManyToManyField(User, through='MealRating',related_name='meal_ratings')

    @property
    def is_favorite(self):
        """Create favorite property from logic"""
        return self.__is_favorite

    @is_favorite.setter
    def is_favorite(self, value):
        self.__is_favorite = value

    @property
    def user_rating(self):
        """Create user_rating property from logic"""
        return self.__user_rating

    @user_rating.setter
    def user_rating(self, value):
        self.__user_rating = value

    @property
    def avg_rating(self):
        """Create avg_rating property from logic"""
        return self.__avg_rating

    @avg_rating.setter
    def avg_rating(self, value):
        self.__avg_rating = value

    # DONE: Establish a many-to-many relationship with User through the appropriate join model
    # DONE: Add an user_rating custom properties
    # DONE: Add an avg_rating custom properties
