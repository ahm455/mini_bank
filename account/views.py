from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Account
from django.contrib.auth.hashers import make_password, check_password
from .forms import AccountForm

def signup(request):
    if request.method == "POST":
        form = AccountForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")

            if Account.objects.filter(email=email).exists():
                messages.error(request, "Email already registered")
                return render(request, "signup.html", {"form": form})

            account = form.save(commit=False)
            account.password = make_password(form.cleaned_data.get("password"))
            account.balance = getattr(account, "balance", 0)
            account.save()

            messages.success(request, "Account created! Please login.")
            return redirect("login")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AccountForm()

    return render(request, "signup.html", {"form": form})

def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = Account.objects.get(email=email)
            if check_password(password, user.password):
                request.session["user_id"] = user.id
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid email or password")
        except Account.DoesNotExist:
            messages.error(request, "Invalid email or password")

    return render(request, "login.html")


def dashboard(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    try:
        user = Account.objects.get(id=user_id)
    except Account.DoesNotExist:
        messages.error(request, "User not found")
        return redirect("login")

    if request.method == "POST":
        action = request.POST.get("action")
        amount_str = request.POST.get("amount")
        try:
            amount = float(amount_str)
            if action == "deposit":
                user.deposit(amount)
                messages.success(request, f"{amount} deposited successfully")
            elif action == "withdraw":
                user.withdraw(amount)
                messages.success(request, f"{amount} withdrawn successfully")
            else:
                messages.error(request, "Invalid action")
        except ValueError:
            messages.error(request, "Please enter a valid number")
        except Exception as e:
            messages.error(request, str(e))

    # Fetch transaction history (latest first)
    transactions = user.transactions.order_by("-date")  # Assuming a 'date' field

    return render(
        request,
        "dashboard.html",
        {"user": user, "transactions": transactions}
    )
def logout(request):
    if "user_id" in request.session:
        del request.session["user_id"]
    return redirect("login")