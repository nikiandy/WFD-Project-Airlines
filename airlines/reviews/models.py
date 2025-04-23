from django.db import models
from django.conf import settings
from flights.models import Flight, FlightSchedule
from django.core.validators import MinValueValidator, MaxValueValidator

# Review model - stores data for review entities
class Review(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='reviews')
    schedule = models.ForeignKey(FlightSchedule, on_delete=models.SET_NULL, related_name='reviews', null=True, blank=True)

    title = models.CharField(max_length=100)
    content = models.TextField()

    overall_rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    staff_rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comfort_rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    food_rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    entertainment_rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    value_rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # String representation of the model
    def __str__(self):
        return f"Review by {self.user.get_full_name()} for flight {self.flight.flight_number}"

    def get_average_rating(self):

        ratings = [
            self.overall_rating,
            self.staff_rating,
            self.comfort_rating,
            self.food_rating,
            self.entertainment_rating,
            self.value_rating
        ]
        return sum(ratings) / len(ratings)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ['-created_at']
        unique_together = ['user', 'flight', 'schedule']

# ReviewComment model - stores data for reviewcomment entities
class ReviewComment(models.Model):

    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='review_comments')

    content = models.TextField()

    is_approved = models.BooleanField(default=False)
    is_staff_response = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # String representation of the model
    def __str__(self):
        return f"Comment by {self.user.get_full_name()} on {self.review}"

    class Meta:
        verbose_name = "Review Comment"
        verbose_name_plural = "Review Comments"
        ordering = ['created_at']

# ReviewHelpfulness model - stores data for reviewhelpfulness entities
class ReviewHelpfulness(models.Model):

    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpfulness_votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='review_helpfulness_votes')
    is_helpful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # String representation of the model
    def __str__(self):
        helpful_text = "helpful" if self.is_helpful else "not helpful"
        return f"{self.user.get_full_name()} found review {self.review.id} {helpful_text}"

    class Meta:
        verbose_name = "Review Helpfulness Vote"
        verbose_name_plural = "Review Helpfulness Votes"
        unique_together = ['review', 'user'] 