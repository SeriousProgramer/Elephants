from django.db import models

class Conversation(models.Model):
    foods_raw  = models.TextField()
    diet_label = models.CharField(max_length=20)    # "vegan", "vegetarian", "non-veg"
    created_at = models.DateTimeField(auto_now_add=True)

    @property          # convenient property for Step 5
    def is_veg(self):
        return self.diet_label in ("vegan", "vegetarian")

