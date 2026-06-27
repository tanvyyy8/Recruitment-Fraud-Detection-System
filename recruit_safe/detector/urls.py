from django.urls import path
from . import views

urlpatterns = [

    path('', views.landing, name='landing'),

    path('login', views.login_view),
    path('signup', views.signup),
    path('logout', views.logout_view),

    path('dashboard', views.dashboard),
    path('analyze', views.analyze),
    path('history', views.history),
    path('settings', views.settings),
    path('change-password', views.change_password),

    path('analyze-text', views.analyze_text),
    path('analyze-image', views.analyze_image),
    path('analyze-link', views.analyze_link),

    path('save-analysis', views.save_analysis),

    path("delete-history/<int:id>/", views.delete_history, name="delete_history"),

    path("manage-users", views.manage_users),
    path("delete-user/<int:id>/", views.delete_user),
    path("change-role/<int:id>/", views.change_role),

]