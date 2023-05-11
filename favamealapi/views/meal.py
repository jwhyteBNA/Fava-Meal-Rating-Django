"""View module for handling requests about meals"""
from rest_framework.exceptions import ValidationError
from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from django.db.models import Avg
from django.contrib.auth.models import User
from favamealapi.models import Meal, MealRating, Restaurant
from favamealapi.views.restaurant import RestaurantSerializer



class MealSerializer(serializers.ModelSerializer):
    """JSON serializer for meals"""
    restaurant = RestaurantSerializer(many=False)

    class Meta:
        model = Meal
        # DONE: Add 'user_rating', 'avg_rating', 'is_favorite' fields to MealSerializer
        fields = ('id', 'name', 'restaurant', 'ratings','user_rating', 'favorites', 'avg_rating', 'is_favorite')

class MealView(ViewSet):
    """ViewSet for handling meal requests"""

    def create(self, request):
        """Handle POST operations for meals

        Returns:
            Response -- JSON serialized meal instance
        """
        try:
            meal = Meal.objects.create(
                name=request.data["name"],
                restaurant=Restaurant.objects.get(
                    pk=request.data["restaurant_id"])
            )
            serializer = MealSerializer(meal)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single meal

        Returns:
            Response -- JSON serialized meal instance
        """
        try:
            user = User.objects.get(username=request.auth.user)
            meal = Meal.objects.get(pk=pk)
            try:
                mealrating = MealRating.objects.get(user_id=user, meal_id=meal)
                meal.user_rating = mealrating.rating
            except MealRating.DoesNotExist:
                meal.user_rating = None

            meal.is_favorite = user in meal.favorites.all()
            avg_rating = MealRating.objects.filter(meal_id=meal).aggregate(Avg('rating'))
            meal.avg_rating = avg_rating['rating__avg']

            # DONE: Get the rating for current user and assign to `user_rating` property

            # DONE: Get the average rating for requested meal and assign to `avg_rating` property

            # DONE: Assign a value to the `is_favorite` property of requested meal

            serializer = MealSerializer(meal)
            return Response(serializer.data)
        except Meal.DoesNotExist as ex:
            return Response({"reason": ex.message}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handle GET requests to meals resource

        Returns:
            Response -- JSON serialized list of meals
        """
        meals = Meal.objects.all()
        user = User.objects.get(username=request.auth.user)

        for meal in meals:
            try:
                mealrating = MealRating.objects.get(user_id=user, meal_id=meal)
                meal.user_rating = mealrating.rating
            except MealRating.DoesNotExist:
                meal.user_rating = None
            meal.is_favorite = user in meal.favorites.all()

            avg_rating = MealRating.objects.filter(meal_id=meal).aggregate(Avg('rating'))
            meal.avg_rating = avg_rating['rating__avg'] if avg_rating['rating__avg'] is not None else 0
        # DONE: Assign a value to the `is_favorite` property of each meal
        # DONE: Get the rating for current user and assign to `user_rating` property

        # DONE: Get the average rating for each meal and assign to `avg_rating` property

        serializer = MealSerializer(meals, many=True)
        return Response(serializer.data)


#do we need to use create functionality to add to bridge table?
    @action(methods=['post', 'put', 'delete'], detail=True)
    def rate(self, request, pk):
        """Post/put request for a user to rate a meal"""
        user=User.objects.get(username=request.auth.user)
        meal = Meal.objects.get(pk=pk)
        rating_value = request.data.get('rating')
        if request.method == 'POST':
            if MealRating.objects.filter(user=user, meal=meal).exists():
                return Response({'message: You have already rated this meal.'})
            else:
                MealRating.objects.create(rating=rating_value, user=user, meal=meal)
                return Response({'message': 'Rating Recorded!'}, status=status.HTTP_201_CREATED)
        elif request.method =='PUT':
            update_rating = MealRating.objects.get(user=user, meal=meal)
            update_rating.rating=rating_value
            update_rating.save()
            return Response({'message': 'Rating Updated!'}, status=status.HTTP_204_NO_CONTENT)
        # elif request.method == 'DELETE':
        #     meal.ratings.remove(user)
        #     return Response({'message': 'User Rating Gone!'}, status=status.HTTP_204_NO_CONTENT)

    # DONE: Add a custom action named `rate` that will allow a client to send a
    #  POST and a PUT request to /meals/3/rate with a body of..
    #       {
    #           "rating": 3
    #       }
    # If the request is a PUT request, then the method should update the user's rating instead of creating a new one

    @action(methods=['post'], detail=True)
    def favorite(self, request, pk):
        """Post request for a user to favorite a meal"""
        user=User.objects.get(username=request.auth.user)
        meal = Meal.objects.get(pk=pk)
        meal.favorites.add(user)
        return Response({'message': 'Meal is a winner!'}, status=status.HTTP_201_CREATED)
    # DONE: Add a custom action named `favorite` that will allow a client to send a
    #  POST request to /meals/3/favorite and add the meal as a favorite

    @action(methods=['delete'], detail=True)
    def unfavorite(self, request, pk):
        """Delete request for a user to unfavorite a meal"""
        user=User.objects.get(username=request.auth.user)
        meal = Meal.objects.get(pk=pk)
        meal.favorites.remove(user)
        return Response({'message': 'Meal is gorbage!'}, status=status.HTTP_204_NO_CONTENT)
    # DONE: Add a custom action named `favorite` that will allow a client to send a
    #  POST request to /meals/3/favorite and add the meal as a favorite

    # DONE: Add a custom action named `unfavorite` that will allow a client to send a
    # DELETE request to /meals/3/unfavorite and remove the meal as a favorite
