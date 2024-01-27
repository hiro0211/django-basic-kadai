"""
URL configuration for creditmanagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from crud import views
from crud.views import calculate_total, CategorySubjectListView, get_department_choices

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.TopView.as_view(), name="top"),
    path('crud/', views.SubjectListView.as_view(), name="list"),
    path('crud/new/', views.SubjectCreateView.as_view(), name="new"),
    path('crud/edit/<int:pk>', views.SubjectUpdateView.as_view(), name="edit"),
    path('crud/delete/<int:pk>', views.SubjectDeleteView.as_view(), name="delete"),
    path('crud/delete/all', views.SubjectDeleteAllView.as_view(), name="delete_all"),
    path('crud/detail/<int:pk>', views.SubjectDetailView.as_view(), name="detail"),
    path('crud/<str:category>/', CategorySubjectListView.as_view(), name="category-subject-list"),
    path('signup/', views.SignUpView.as_view(), name="signup"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path('total/', calculate_total, name="total"),
    path('unipa_register/', views.LoadDataFromSite.as_view(), name="unipa_register"),
    path('password_change/', views.PasswordChange.as_view(), name="password_change"),
    path('password_change/done/', views.PasswordChangeDone.as_view(), name="password_change_done"),
    path('password_reset/', views.MyPasswordReset.as_view(), name="password_reset"),
    path('password_reset/done/', views.MyPasswordResetDone.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.MyPasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.MyPasswordResetComplete.as_view(), name='password_reset_complete'),
    path('profile/', views.StudentProfileView.as_view(), name='profile'),
    path('profile/change/', views.StudentChangeView.as_view(), name='profile_change'),
    path('signup/', get_department_choices, name='signup')
]
