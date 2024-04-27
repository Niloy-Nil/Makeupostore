from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .models import Customer, Product, Cart, OrderPlaced, feedback, leaderboard, Contact
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from decimal import Decimal
from django.db.models import Avg

class ProductView(View):
    def get(self, request):
        lead_users = leaderboard.objects.filter(leaderScore__gt=20).order_by('-leaderScore')
        
        totalitem = 0
        hdmakeup = Product.objects.filter(category='HM')
        mattemakeup = Product.objects.filter(category='MM')
        facewash = Product.objects.filter(category='M')
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'app/home.html', {'hdmakeup': hdmakeup, 'mattemakeup': mattemakeup, 'facewash': facewash, 'totalitem': totalitem, "lead_users":lead_users})


class ProductDetailView(View):
    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return redirect('product-detail', pk=pk)

        total_item = 0
        item_already_in_cart = False
        feedback_data = None
        order = None  # Define order with a default value of None
        lead_users = leaderboard.objects.filter(leaderScore__gt=20).order_by('-leaderScore')
        if request.user.is_authenticated:
            feedback_data = feedback.objects.filter(product=pk)
            order = OrderPlaced.objects.filter(product=pk, user=request.user.id)
           
            total_item = Cart.objects.filter(user=request.user).count()
            item_already_in_cart = Cart.objects.filter(Q(product=product) & Q(user=request.user)).exists()

        context = {
            'product': product,
            'item_already_in_cart': item_already_in_cart,
            'total_item': total_item,
            'feedback_data': feedback_data,
            'order': order,
            "lead_users":lead_users
        }

        return render(request, 'app/productdetail.html', context)


@login_required()
def add_to_cart(request):
    user = request.user
    item_already_in_cart1 = False
    product = request.GET.get('prod_id')
    item_already_in_cart1 = Cart.objects.filter(Q(product=product) & Q(user=request.user)).exists()
    if not item_already_in_cart1:
        product_title = Product.objects.get(id=product)
        Cart(user=user, product=product_title).save()
        messages.success(request, 'Product Added to Cart Successfully !!' )
        return redirect('/cart')
    else:
        return redirect('/cart')
 

@login_required
def show_cart(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        user = request.user
        cart = Cart.objects.filter(user=user)

        amount = 0.0
        shipping_amount = 70.0
        totalamount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        
        lead_users = leaderboard.objects.filter(leaderScore__gt=20).order_by('-leaderScore')
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.selling_price)
                amount += tempamount
                totalamount = amount + shipping_amount
              

            return render(request, 'app/addtocart.html', {'carts': cart, 'amount': amount, 'totalamount': totalamount, 'totalitem': totalitem, "lead_users":lead_users})
        else:
            return render(request, 'app/emptycart.html', {'totalitem': totalitem, "lead_users":lead_users})
    else:
        return render(request, 'app/emptycart.html', {'totalitem': totalitem, "lead_users":lead_users})


def plus_cart(request):
	if request.method == 'GET':
		prod_id = request.GET['prod_id']
		c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
		c.quantity+=1
		c.save()
		amount = 0.0
		shipping_amount= 70.0
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		for p in cart_product:
			tempamount = (p.quantity * p.product.discounted_price)
		
			amount += tempamount
		data = {
			'quantity':c.quantity,
			'amount':amount,
			'totalamount':amount+shipping_amount
		}
		return JsonResponse(data)
	else:
		return HttpResponse("")

def minus_cart(request):
	if request.method == 'GET':
		prod_id = request.GET['prod_id']
		c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
		c.quantity-=1
		c.save()
		amount = 0.0
		shipping_amount= 70.0
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		for p in cart_product:
			tempamount = (p.quantity * p.product.discounted_price)
			amount += tempamount
		data = {
			'quantity':c.quantity,
			'amount':amount,
			'totalamount':amount+shipping_amount
		}
		return JsonResponse(data)
	else:
		return HttpResponse("")

@login_required
def checkout(request):
    user = request.user

    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=request.user)
    lead_users = leaderboard.objects.filter(leaderScore__gt=20).order_by('-leaderScore')
    leaderboard_entry = leaderboard.objects.filter(user=user).first()
    
    # Check if qualify
    if leaderboard_entry:
        score = analyzer(leaderboard_entry.leaderScore)
    else:
        score = 0
    
    total_original_price = Decimal(0)
    total_discounted_price = Decimal(0)
    per_item_discount_price = {}  # Dictionary to store per-item discounted prices
    for item in cart_items:
        original_price = Decimal(item.product.selling_price) * Decimal(item.quantity)
        total_original_price += original_price
        

        # Apply discount if the user qualifies
        if score == 20:
           
            discounted_price = original_price * Decimal('0.8')  # 20% discount
            per_item_discount_price[item.id] = discounted_price  # Store discounted price by item ID
        else:
            per_item_discount_price[item.id] = original_price  # Store original price by item ID
            
        total_discounted_price += per_item_discount_price[item.id]
    
    return render(request, 'app/checkout.html', {'add': add, 'cart_items': cart_items, "lead_users": lead_users, 'total_original_price': total_original_price, 'total_discounted_price': total_discounted_price, "discount_for_score":score, "per_item_discount_price":per_item_discount_price})



@login_required
def sp_checkout(request, id):
    user = request.user
    try:
        # Retrieve the product object
        product = Product.objects.get(id=id)
        
        # Retrieve the customer object
        add = Customer.objects.filter(user=user)
        
        # Retrieve a single leaderboard object for the user
        leaderboard_entry = leaderboard.objects.filter(user=user).first()
        lead_users = leaderboard.objects.filter(leaderScore__gt=20).order_by('-leaderScore')
        
        # Check if leaderboard_entry exists before accessing its attributes
        if leaderboard_entry:
            score = analyzer(leaderboard_entry.leaderScore)
        else:
            score = 0
            
        # Calculate the discounted price based on the original price and the discount percentage
        discount_percentage = 20  # Assuming a 20% discount
        discounted_price = product.selling_price * (1 - discount_percentage / 100)
        # Calculate the discount amount
        discount_amount = product.selling_price - discounted_price
        
    except Product.DoesNotExist:
        return redirect("product-detail", pk=id)

    return render(request, 'app/checkout.html', {"sp_cart_items": [product], "proid": id, "add": add, "discount": score, "discounted_price": discounted_price, "discount_amount": discount_amount, "lead_users":lead_users})


@login_required
def sp_payment_done(request, product_id):
    user = request.user
    
    try:
        product = get_object_or_404(Product, id=product_id)
        customer = Customer.objects.get(user=user)
        
        order_spec = create_order(user, customer, product)
        update_leaderboard(user, order_spec.product.selling_price)
        
    except Product.DoesNotExist:
        print("Product with ID", product_id, "does not exist")
    
    return redirect("orders")

@login_required
def payment_done(request):
    if request.method == "POST":
        
        user = request.user
        
        try:
            customer = Customer.objects.get(user=user)
            
            for cart_item in Cart.objects.filter(user=user):
                order_spec = create_order(user, customer, cart_item.product, cart_item.quantity)
                update_leaderboard(user, order_spec.product.selling_price)
                cart_item.delete()
        
        except Customer.DoesNotExist:
            print("Customer with ID", user, "does not exist")

        return redirect("orders")


def remove_cart(request):
	if request.method == 'GET':
		prod_id = request.GET['prod_id']
		c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
		c.delete()
		amount = 0.0
		shipping_amount= 70.0
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		for p in cart_product:
			tempamount = (p.quantity * p.product.discounted_price)
			amount += tempamount
		data = {
			'amount':amount,
			'totalamount':amount+shipping_amount
		}
		return JsonResponse(data)
	else:
		return HttpResponse("")

@login_required
def address(request):
    totalitem = 0
    lead_users = leaderboard.objects.filter(leaderScore__gt=20).order_by('-leaderScore')
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'add': add, 'active': 'btn-primary', 'totalitem': totalitem, "lead_users":lead_users})

@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    lead_users = leaderboard.objects.filter(leaderScore__gt=20).order_by('-leaderScore')
    return render(request, 'app/orders.html', {'order_placed': op, "lead_users":lead_users})

def mobile(request, data=None):
    # Initialize totalitem count
    totalitem = 0
    lead_users = leaderboard.objects.filter(leaderScore__gt=20).order_by('-leaderScore')
    # If user is authenticated, count total items in the cart
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()

    # Filter products based on the provided data
    if data is None:
        # If no data provided, show all mobile products
        products = Product.objects.filter(category='M')
    elif data in ['Redmi', 'Samsung']:
        # If brand data provided, filter by brand
        products = Product.objects.filter(category='M', brand=data)
    elif data == 'below':
        # If below data provided, filter products below a certain price
        products = Product.objects.filter(category='M', discounted_price__lt=10000)
    elif data == 'above':
        # If above data provided, filter products above a certain price
        products = Product.objects.filter(category='M', discounted_price__gt=10000)
    else:
        # Handle unrecognized data with an error message
        return render(request, 'app/error.html', {'message': 'Invalid data'})

    # Render the template with the filtered products and totalitem count
    return render(request, 'app/mobile.html', {'products': products, 'totalitem': totalitem, "lead_users":lead_users})

class CustomerRegistrationView(View):
 def get(self, request):
  form = CustomerRegistrationForm()
  return render(request, 'app/customerregistration.html', {'form':form})
  
 def post(self, request):
  form = CustomerRegistrationForm(request.POST)
  if form.is_valid():
   messages.success(request, 'Congratulations!! Registered Successfully.')
   form.save()
  return render(request, 'app/customerregistration.html', {'form':form})

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        totalitem = 0
        leadscore = None  # Define leadscore with a default value of None
        lead_users = leaderboard.objects.filter(leaderScore__gt=20).order_by('-leaderScore')
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            leadscore = leaderboard.objects.filter(user=request.user).first()
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary', 'totalitem': totalitem, 'score': leadscore, 'lead_users': lead_users})
        
    def post(self, request):
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=usr, name=name, locality=locality, city=city, state=state, zipcode=zipcode)
            reg.save()  # Saving Customer object associated with the user
            messages.success(request, 'Congratulations!! Profile Updated Successfully.')
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary', 'totalitem': totalitem})


def filter_products(request):
    # Get the search query from the request
    query = request.GET.get("q")
    lead_users = leaderboard.objects.filter(leaderScore__gt=20).order_by('-leaderScore')
    # Filter products based on title or category
    results = Product.objects.filter(Q(title__icontains=query) | Q(category=query))

    # Check if any products are found
    if results:
        # If results are found, prepare context for rendering the template
        context = {
            "products": results,
            "query": query,  # Passing the query for displaying in the template
        }
    else:
        # If no results are found, provide a message to the user
        context = {
            "message": "No products found for the query: {}".format(query),
            "query": query,  # Passing the query for displaying in the template
            'lead_users': lead_users
        }

    # Render the template with the context
    return render(request, 'app/search.html', context)
# View for providing feedback on a product
@login_required
def feed_back(request, pro_id):
    if request.method == "POST":
        rating = request.POST.get("exp")
        experience = request.POST.get("msg")
        
        try:
            product = Product.objects.get(id=pro_id)
        except Product.DoesNotExist:
            # Redirect to product detail page if product not found
            return redirect("product-detail", pk=pro_id)

        # Validate input
        if not rating or not experience:
            return redirect("product-detail", pk=pro_id)
        
        try:
            # Create Feedback object
            feedback_instance = feedback.objects.create(
                user=request.user,
                rate_num=rating,
                experience=experience,
                product=product
            )
            # Redirect to product detail page after successful feedback submission
            return redirect("product-detail", pk=pro_id)
        except Exception as e:
            # Handle exceptions gracefully
            return redirect("product-detail", pk=pro_id)

    # Render a form for submitting feedback
    return redirect("product-detail", pk=pro_id)

# Helper function for processing checkout for a product
@login_required
def sq_checkout_helper(request, id=None):
    if request.method == "POST":
        user = request.user
        full_name = request.POST.get("fullname")
        address = request.POST.get("address")
        city = request.POST.get("city")
        zipcode = request.POST.get("zipcode")
        state = request.POST.get("state")

        if full_name and address and city and zipcode and state:
            # Create Customer object
            Customer.objects.create(
                user=user,
                name=full_name,
                locality=address,
                city=city,
                zipcode=zipcode,
                state=state
            )
            print("Customer created")
            return redirect("spcheckout", id=id)
        else:
            print("Please provide all fields")
            return redirect("spcheckout", id=id)

# Helper function for processing checkout
@login_required
def checkout_helper(request):
    if request.method == "POST":
        user = request.user
        full_name = request.POST.get("fullname")
        address = request.POST.get("address")
        city = request.POST.get("city")
        zipcode = request.POST.get("zipcode")
        state = request.POST.get("state")

        if full_name and address and city and zipcode and state:
            # Create Customer object
            Customer.objects.create(
                user=user,
                name=full_name,
                locality=address,
                city=city,
                zipcode=zipcode,
                state=state
            )
            print("Customer created")
            return redirect("checkout")
        else:
            print("Please provide all fields")
            return redirect("checkout")

# View for displaying leaderboard and contact form
@method_decorator(login_required, name='dispatch')
class Contactor(View):
    def get(self, request, *args, **kwargs):
        # Fetch users with a leaderboard score greater than 20 and order by score
        lead_users = leaderboard.objects.filter(leaderScore__gt=20).order_by('-leaderScore')
        return render(request, 'app/contact.html', {"lead_users": lead_users})
    
    def post(self, request, *args, **kwargs):
        full_name = request.POST.get("fullname")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("msg")

        if full_name and email and subject and message:
            # Create Contact object
            Contact.objects.create(
                user=request.user,
                full_name=full_name,
                email=email,
                subject=subject,
                message=message
            )
            return redirect("contact")
        else:
            print("Please provide all credentials")
            # Use message framework for displaying error message
            return redirect("contact")

# Function for creating an order
def create_order(user, customer, product, quantity=1):
    return OrderPlaced.objects.create(
        user=user,
        customer=customer,
        product=product,
        quantity=quantity
    )

# Function for updating leaderboard
def update_leaderboard(user, price):
    # Update the leaderboard score based on the price of the purchased item
    leaderboard_entry, created = leaderboard.objects.get_or_create(user=user)
    leaderboard_entry.leaderScore += calculate_leader_score(price)
    
    # Update the last_purchase_date for the user
    leaderboard_entry.last_purchase_date = timezone.now()
    leaderboard_entry.save()

# Function for calculating leaderboard score
def calculate_leader_score(price):
    # Calculate the leaderboard score based on the price of the purchased item
    if price > 10000:
        return 10
    elif price > 5000:
        return 20
    elif price >= 5000:
        return 5
    else:
        return 2

# Function for analyzing leaderboard score and providing discount
def analyzer(score):
    if score >= 20:
        # Return 20 percentage discount
        return 20
    else:
        return 0


def filter_by_rating(request, stars):
    # Convert stars to an integer
    stars = int(stars)
    print(stars)
    # Filter products based on average rating
    products = Product.objects.annotate(avg_rating=Avg('Product__rate_num')).filter(avg_rating__gte=stars)
    print(products)
    # Render the template with filtered products
    return render(request, 'app/mobile.html', {'products': products})