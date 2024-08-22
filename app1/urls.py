from django.urls import path
from . import views

app_name = "app1"

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_user, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout_user, name="logout"),
    path("create_quiz/", views.create_quiz, name="create_quiz"),
    path("quiz_details/<int:quiz_id>/", views.quiz_details, name="quiz_details"),
    path("take_quiz/<int:quiz_id>/", views.takequizview, name="take_quiz"),
    path("results/<int:quiz_id>/", views.resultsview, name="results"),
    path("user-profile/", views.user_profile_view, name="user_profile"),
    path("add_question/<int:quiz_id>", views.add_question, name="add_question"),
    path("allquizzes/", views.list_all_quizzes, name="allquizzes"),
    path("archived/", views.list_archived_quizzes, name="archived"),
    path("my_quizzes/", views.my_quizzes, name="my_quizzes"),
]
