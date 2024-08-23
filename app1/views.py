from django.core.files.storage import default_storage
from PIL import Image
import math
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.db.models import Avg, Sum
from django.urls import reverse
from django.contrib.auth.decorators import login_required


from .models import (
    User,
    Category,
    Quiz,
    Question,
    Choice,
    UserAnswer,
    Score,
)


# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return redirect("app1:login")

    availablequizzes = Quiz.objects.filter(status=True)
    return render(
        request,
        "app1/index.html",
        {
            "available_quizzes": availablequizzes,
        },
    )


def list_all_quizzes(request):
    allquizzes = Quiz.objects.filter(archived=False)
    return render(
        request,
        "app1/all_quizzes.html",
        {
            "allquizzes": allquizzes,
        },
    )


def list_archived_quizzes(request):
    archived_quizzes = Quiz.objects.filter(archived=True)
    return render(
        request,
        "app1/archived.html",
        {
            "quizlist": archived_quizzes,
        },
    )


def my_quizzes(request):
    if not request.user.is_authenticated:
        return redirect("app1:login")

    user = request.user

    # Created Quizzes
    created_quizzes = Quiz.objects.filter(auther=user)

    # Participated Quizzes (assuming participation through answered questions)
    participated_quizzes = Quiz.objects.filter(score__user=user).distinct()

    context = {
        "created_quizzes": created_quizzes,
        "participated_quizzes": participated_quizzes,
    }

    return render(request, "app1/my_quizzes.html", context)


def create_quiz(request):
    if not request.user.is_authenticated:
        return redirect("app1:login")

    categories = Category.objects.all()
    if request.method == "POST":
        quiztitle = request.POST.get("quiz-title")
        quizdescription = request.POST.get("quiz-description")
        timelimit = request.POST.get("time-limit")
        difficulty = request.POST.get("difficulty-level")
        categoryname = request.POST.get("category")

        category = get_object_or_404(Category, name=categoryname)

        newquiz = Quiz.objects.create(
            title=quiztitle,
            description=quizdescription,
            difficulty_level=difficulty,
            category=category,
            time_limit=timelimit,
        )
        newquiz.save()

        return redirect(
            reverse(
                "app1:add_question",
                kwargs={
                    "quiz_id": newquiz.id,
                },
            )
        )
    else:
        return render(
            request,
            "app1/create_quiz.html",
            {
                "categories": categories,
            },
        )


def add_question(request, quiz_id):
    newquiz = get_object_or_404(Quiz, pk=quiz_id)
    return render(
        request,
        "app1/add_questions.html",
        {
            "quiz": newquiz,
        },
    )


def quiz_details(request, quiz_id):
    curr_quiz = get_object_or_404(Quiz, pk=quiz_id)
    total_points = 0
    num_questions = 0
    for question in curr_quiz.question_set.all():
        total_points += question.points
        num_questions += 1
    if curr_quiz is not None:
        return render(request, "app1/quiz_details.html", {
            "quiz": curr_quiz,
            'points': total_points,
            'num_questions': num_questions,
        },)


@login_required
def takequizview(request, quiz_id):
    if request.method == "GET":
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        questions = quiz.question_set.all()
        return render(request, "app1/take_quiz.html", {
                "quiz": quiz,
                "questions": questions,
        },)
    return redirect('app1:results')


def resultsview(request, quiz_id):
    score = 0
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    all_questions = quiz.question_set.all()
    num_questions = all_questions.count()
    questions_answered = 0
    total_score = 0
    correct_questions = 0

    for question in all_questions:
        total_score += question.points
        selected_choice = request.POST.get(f"option-{question.id}")
        try:
            choice = Choice.objects.get(pk=selected_choice, question=question)
            if choice.is_correct == True:
                score += question.points
                correct_questions += 1
            questions_answered += 1
        except Choice.DoesNotExist:
            pass

    user = request.user
    # create a Score entry
    Score.objects.create(
        user=user,
        quiz=quiz,
        score=score,
    ).save()

    percentage = math.ceil((score / total_score) * 100) 
    context = {
        "score": score,
        "total_questions": num_questions,
        'questions_answered': questions_answered,
        'total_score': total_score,
        'correct_questions': correct_questions,
        "percentage": percentage,
    }
    return render(request, "app1/results.html", context)


def user_profile_view(request):
    user = request.user

    if request.method == 'POST':
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            # Save the original image to the media directory
            image_path = default_storage.save(profile_picture.name, profile_picture)
            image = Image.open(default_storage.path(image_path))

            # Resize the image to 400x400 pixels
            image = image.resize((400, 400), Image.ANTIALIAS)

            # Save the resized image back to the media directory
            resized_image_path = default_storage.save(f"resized_{image_path}", image)

            # Update the user's profile picture field
            user.profile_picture = resized_image_path
            user.save()

    else:
        scorelist = Score.objects.filter(user=user, score__isnull=False)

        total_score_so_far = 0
        total_quiz_attemps = scorelist.count()
        total_points = 0

        total_contribution = Quiz.objects.filter(auther=user).count()

        for scoreobj in scorelist:
            total_score_so_far += scoreobj.score
            
            for question in scoreobj.quiz.question_set.all():
                    total_points += question.points

        average_score = 0
        if total_points is not 0:
            average_score = (total_score_so_far/total_points) * 100
        average_score = math.ceil(average_score)

        context = {
            'user': user,
            'total_attempts': total_quiz_attemps,
            'average_score': average_score,
            'quizzes_created': total_contribution,
        }

        return render(request, 'app1/user_profile.html', context)


def login_user(request):
    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("app1:index")
        return render(
            request,
            "app1/login.html",
            {
                "err_message": "Invalid username or password",
            },
        )
    return render(request, "app1/login.html")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']

        # Attempt to create new user
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=firstname,
                last_name=lastname,
                email=email
            )
            user.save()
        except IntegrityError:
            return render(request, "app1/register.html", {
                "err_message": "Username already taken."},
            )
        login(request, user)
        return redirect("app1:index")
    return render(request, "app1/register.html")


def logout_user(request):
    logout(request)
    return redirect("app1:login")
