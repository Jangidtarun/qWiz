from django.shortcuts import render, redirect, get_object_or_404
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
    if curr_quiz is not None:
        return render(
            request,
            "app1/quiz_details.html",
            {
                "quiz": curr_quiz,
            },
        )


@login_required
def takequizview(request, quiz_id):
    if request.method == "GET":
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        questions = quiz.question_set.all()
        return render(
            request,
            "app1/take_quiz.html",
            {
                "quiz": quiz,
                "questions": questions,
            },
        )


def resultsview(request, quiz_id):
    if request.method == "POST":
        score = 0
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        all_questions = quiz.question_set.all()
        num_questions = all_questions.count()

        for question in all_questions:
            selected_choice = request.POST.get(f"option-{question.id}")
            try:
                choice = Choice.objects.get(
                    pk=selected_choice, question=question, is_correct=True
                )
                if choice:
                    score += 1
            except Choice.DoesNotExist:
                pass

        user = request.user
        # Update or create a Score entry
        score_obj, created = Score.objects.get_or_create(user=user, quiz=quiz)
        score_obj.attempts += 1
        score_obj.score = score
        score_obj.save()

        percentage = (score / num_questions) * 100
        context = {
            "score": score,
            "total_questions": num_questions,
            "percentage": percentage,
        }
        return render(request, "app1/results.html", context)


def user_profile_view(request):
    user = request.user

    # Total attempts
    total_attempts = Score.objects.filter(user=user).aggregate(Sum('attempts'))['attempts__sum'] or 0

    # Total time spent (approximation based on quiz time limits)
    total_time_spent = sum(Score.objects.filter(user=user).values_list('quiz__time_limit', flat=True))

    # Average score
    average_score = Score.objects.filter(user=user).exclude(score__isnull=True).exclude(score=0).aggregate(Avg('score'))['score__avg'] or 0
    context = {
        'user': user,
        'total_attempts': total_attempts,
        'total_time_spent': total_time_spent,
        'average_score': average_score,
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

        # Ensure password matches confirmation
        password = request.POST["password"]
        # confirmation = request.POST["confirmation"]
        # if password != confirmation:
        #     return render(request, "app1/register.html", {
        #         "message": "Passwords must match."
        #     })

        # Attempt to create new user
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
            )
            user.save()
        except IntegrityError:
            return render(
                request,
                "app1/register.html",
                {"err_message": "Username already taken."},
            )
        login(request, user)
        return redirect("app1:index")
    return render(request, "app1/register.html")


def logout_user(request):
    logout(request)
    return redirect("app1:login")
