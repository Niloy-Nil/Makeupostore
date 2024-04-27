from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .forms import LoginForm, MyPasswordChangeForm, MyPasswordResetForm, MySetPasswordForm
urlpatterns = [
    # path('', views.home),
    path('', views.ProductView.as_view(), name="home"),
    # path('product-detail', views.product_detail, name='product-detail'),
    path('product-detail/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('cart/', views.show_cart, name='showcart'),
    path('pluscart/', views.plus_cart),
    path('minuscart/', views.minus_cart),
    path('removecart/', views.remove_cart),
    # Handle Multiple cart checkouts
    path('checkout/', views.checkout, name='checkout'),
    path('checkout-helper-agent/', views.checkout_helper, name='mhelpcheckout'),
    # Handle single page checkout
    path('checkout/<int:id>/', views.sp_checkout, name='spcheckout'),
    path('checkout-helper-agent/<int:id>/', views.sq_checkout_helper, name='shelpcheckout'),


    path('address/', views.address, name='address'),
    path('orders/', views.orders, name='orders'),
    # Specific product done
    path('payment_done/<int:id>/', views.sp_payment_done, name='payment_done'),
    # Cart/Multi product done
    path('paymentdone', views.payment_done, name='paymentdone'),

    path('mobile/', views.mobile, name='mobile'),
    path('mobile/<slug:data>', views.mobile, name='mobiledata'),

    path('accounts/login/', auth_views.LoginView.as_view(template_name='app/login.html', authentication_form=LoginForm), name='login'),
    # path('profile/', views.profile, name='profile'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('passwordchange/', auth_views.PasswordChangeView.as_view(template_name='app/passwordchange.html', form_class=MyPasswordChangeForm, success_url='/passwordchangedone/'), name='passwordchange'),
    path('passwordchangedone/', auth_views.PasswordChangeDoneView.as_view(template_name='app/passwordchangedone.html'), name='passwordchangedone'),
    
    path("password-reset/", auth_views.PasswordResetView.as_view(template_name='app/password_reset.html', form_class=MyPasswordResetForm), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(template_name='app/password_reset_done.html'), name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name='app/password_reset_confirm.html', form_class=MySetPasswordForm), name="password_reset_confirm"),
    path("password-reset-complete/", auth_views.PasswordResetCompleteView.as_view(template_name='app/password_reset_complete.html'), name="password_reset_complete"),

    path('registration/', views.CustomerRegistrationView.as_view(), name='customerregistration'),
    path('search/', views.filter_products, name='search'),
    path('feedback/<int:pro_id>/', views.feed_back, name='feedback'),
    path('leader-board/', views.update_leaderboard, name='leaderboard'),
    path('contact', views.Contactor.as_view(), name='contact'),
    path('filter_by_rating/<int:stars>/', views.filter_by_rating, name='filtersstarts'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
