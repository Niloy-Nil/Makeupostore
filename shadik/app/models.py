from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
STATE_CHOICES = (
  ('Dhaka','Dhaka'),
  ('Chittagong','Chittagong'),
  ('Sylhet',' Sylhet'),
  
)
class Customer(models.Model):
 user = models.ForeignKey(User, on_delete=models.CASCADE)
 name = models.CharField(max_length=200)
 locality = models.CharField(max_length=200)
 city = models.CharField(max_length=50)
 zipcode = models.IntegerField()
 state = models.CharField(choices=STATE_CHOICES, max_length=50)

 def __str__(self):
  # return self.user.username
  return str(self.id)


CATEGORY_CHOICES = (
 ('M', 'Mobile'),
 ('L', 'Laptop'),
 ('MM', 'Matte Makeup'),
 ('HM', 'HD Makeup'),
)
class Product(models.Model):
 title = models.CharField(max_length=100)
 selling_price = models.FloatField()
 discounted_price = models.FloatField()
 description = models.TextField()
 brand = models.CharField(max_length=100)
 category = models.CharField( choices=CATEGORY_CHOICES, max_length=2)
 product_image = models.ImageField(upload_to='productimg')

 def __str__(self):
  return str(self.id)


class Cart(models.Model):
 user = models.ForeignKey(User, on_delete=models.CASCADE)
 product = models.ForeignKey(Product, on_delete=models.CASCADE)
 quantity = models.PositiveIntegerField(default=1)

 def __str__(self):
  return str(self.id)
  
  # Below Property will be used by checkout.html page to show total cost in order summary
 @property
 def total_cost(self):
   return self.quantity * self.product.discounted_price

STATUS_CHOICES = (
  ('Accepted','Accepted'),
  ('Packed','Packed'),
  ('On The Way','On The Way'),
  ('Delivered','Delivered'),
  ('Cancel','Cancel')
)

class OrderPlaced(models.Model):

 user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="User", default=1)
 customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="customer", default="")
 product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product", default="")
 quantity = models.PositiveIntegerField(default=1)
 ordered_date = models.DateTimeField(auto_now_add=True)
 status = models.CharField(max_length=50,choices=STATUS_CHOICES,default='Pending')

  # Below Property will be used by orders.html page to show total cost
 @property
 def total_cost(self):
   return self.quantity * self.product.discounted_price
 
class leaderboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    leaderScore = models.PositiveBigIntegerField(default=0, db_index=True)
    last_purchase_date = models.DateTimeField(null=True, blank=True)
  
class feedback(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, default="")
  product = models.ForeignKey(Product, on_delete=models.CASCADE, default="", related_name="Product")
  rate_num =  models.PositiveIntegerField(db_index=True)
  experience = models.TextField(db_index=True)

class Contact(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, default="")
  full_name = models.CharField(max_length=100, db_index=True)
  email = models.EmailField(db_index=True)
  subject = models.CharField(max_length=200, db_index=True)
  message = models.TextField(db_index=True)
