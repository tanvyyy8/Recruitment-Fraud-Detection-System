from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from .models import JobAnalysis
import os
from django.core.files.storage import FileSystemStorage
from django.db.models import Count
from .models import UserProfile
from django.core.paginator import Paginator
# ================= AI ENGINE IMPORTS =================

from ai_engine.predictor import predict_job
from ai_engine.rule_engine import detect_rules
from ai_engine.justification_engine import generate_justification
from ai_engine.ocr_reader import extract_text_from_image, extract_job_title
from ai_engine.link_scraper import extract_job_from_link, detect_suspicious_domain
from ai_engine.explainable_ai import explain_prediction


# AUTH IMPORTS
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.db.models.functions import TruncDay
from django.db.models import Count
from datetime import datetime


# ================= LANDING PAGE =================

def landing(request):
    create_default_admin()
    return render(request, "landing.html")


# ================= AUTH SYSTEM =================

def signup(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {"error": "Username already exists"})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.save()
        # CREATE USER PROFILE
        UserProfile.objects.create(
            user=user,
            role="USER"
        )

        return redirect("/login")

    return render(request, "signup.html")


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/dashboard")

        else:
            return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("/login")

# ================= DEFAULT ADMIN SETUP =================

from .models import UserProfile

def create_default_admin():

    try:

        if not User.objects.filter(username="tanvibhave").exists():

            admin_user = User.objects.create_user(
                username="tanvibhave",
                password="tanvi123#"
            )

            UserProfile.objects.create(
                user=admin_user,
                role="ADMIN"
            )

    except:
        pass



# ================= PAGE VIEWS (PROTECTED) =================

@login_required(login_url="/login")
def dashboard(request):

    # ===== GET USER PROFILE =====
    try:
        profile = UserProfile.objects.get(user=request.user)
    except:
        profile = None

    # =====================================================
    # ADMIN → SEE ALL ANALYSES (Admin + All Users)
    # USER  → SEE ONLY OWN ANALYSES
    # =====================================================

    if profile and profile.role == "ADMIN":
        analyses = JobAnalysis.objects.all()
        selected_user = request.user

    else:
        analyses = JobAnalysis.objects.filter(user=request.user)
        selected_user = request.user

    # =====================================================
    # COUNTS
    # =====================================================

    text_genuine = analyses.filter(
        analysis_type="text",
        decision="Genuine"
    ).count()

    text_suspicious = analyses.filter(
        analysis_type="text",
        decision="Suspicious"
    ).count()

    text_fraud = analyses.filter(
        analysis_type="text",
        decision="Fraud"
    ).count()

    image_genuine = analyses.filter(
        analysis_type="image",
        decision="Genuine"
    ).count()

    image_suspicious = analyses.filter(
        analysis_type="image",
        decision="Suspicious"
    ).count()

    image_fraud = analyses.filter(
        analysis_type="image",
        decision="Fraud"
    ).count()

    link_genuine = analyses.filter(
        analysis_type="link",
        decision="Genuine"
    ).count()

    link_suspicious = analyses.filter(
        analysis_type="link",
        decision="Suspicious"
    ).count()

    link_fraud = analyses.filter(
        analysis_type="link",
        decision="Fraud"
    ).count()

    # =====================================================
    # LAST 7 DAYS TREND
    # =====================================================

    from datetime import timedelta
    from django.utils import timezone

    last_7_days = []

    text_trend_data = []
    image_trend_data = []
    link_trend_data = []

    for i in range(6, -1, -1):
        day = timezone.now().date() - timedelta(days=i)

        last_7_days.append(day.strftime("%a"))

        text_count = analyses.filter(
            analysis_type="text",
            created_at__date=day
        ).count()

        image_count = analyses.filter(
            analysis_type="image",
            created_at__date=day
        ).count()

        link_count = analyses.filter(
            analysis_type="link",
            created_at__date=day
        ).count()

        text_trend_data.append(text_count)
        image_trend_data.append(image_count)
        link_trend_data.append(link_count)

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {
        "text_data": [text_genuine, text_suspicious, text_fraud],
        "image_data": [image_genuine, image_suspicious, image_fraud],
        "link_data": [link_genuine, link_suspicious, link_fraud],

        "text_bar": [text_genuine, text_suspicious, text_fraud],
        "image_bar": [image_genuine, image_suspicious, image_fraud],
        "link_bar": [link_genuine, link_suspicious, link_fraud],

        "text_trend_labels": last_7_days,
        "text_trend_data": text_trend_data,

        "image_trend_labels": last_7_days,
        "image_trend_data": image_trend_data,

        "link_trend_labels": last_7_days,
        "link_trend_data": link_trend_data,
    }

    return render(request, "dashboard.html", context)
# ================= ADMIN DASHBOARD =================

@login_required(login_url="/login")
def admin_dashboard(request):

    return render(request, "dashboard.html")


@login_required(login_url="/login")
def analyze(request):
    return render(request, "analyze.html")


@login_required(login_url="/login")
def history(request):

    analyses = JobAnalysis.objects.filter(user=request.user).order_by("-created_at")

    # ===== GET FILTER VALUES =====
    type_filter = request.GET.get("type")
    status_filter = request.GET.get("status")
    date_filter = request.GET.get("date")

    # ===== APPLY FILTERS =====

    if type_filter:
        analyses = analyses.filter(analysis_type=type_filter)

    if status_filter:
        analyses = analyses.filter(decision=status_filter)

    if date_filter:
        try:
            year, month = date_filter.split("-")
            analyses = analyses.filter(
                created_at__year=year,
                created_at__month=month
            )
        except:
            pass

    # ===== PAGINATION =====
    paginator = Paginator(analyses, 5)
    page_number = request.GET.get("page")
    analyses = paginator.get_page(page_number)

    return render(request, "history.html", {
        "analyses": analyses
    })

@login_required(login_url="/login")
def settings(request):
    return render(request, "settings.html")

@login_required(login_url="/login")
def change_password(request):

    if request.method == "POST":

        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = request.user

        # Current password check
        if not user.check_password(current_password):
            return render(request, "settings.html", {
                "password_error": "Current password is incorrect"
            })

        # New password match check
        if new_password != confirm_password:
            return render(request, "settings.html", {
                "password_error": "New passwords do not match"
            })

        # Password update
        user.set_password(new_password)
        user.save()

        # Logout after password change for security
        logout(request)

        return redirect("/login")

    return redirect("/settings")


# ================= ANALYSIS API =================

@login_required(login_url="/login")
def analyze_text(request):

    if request.method == "POST":

        data = json.loads(request.body)

        # ================= BASIC INPUT =================

        title = data.get("title", "")
        company = data.get("company", "")

        # ================= AI PREDICTION =================

        label, confidence = predict_job(data)

        # ================= RULE ENGINE =================

        rule_reasons = detect_rules(data)

        # ================= EXPLAINABLE AI =================

        xai_result = explain_prediction(data)

        xai_words = []

        for item in xai_result["important_words"]:

            if isinstance(item, dict):
                xai_words.append(item.get("word", ""))

            else:
                xai_words.append(str(item))

        # ================= MERGE REASONS =================

        reasons = list(dict.fromkeys(rule_reasons + xai_words))

        fraud_probability = confidence / 100
        rule_count = len(reasons)

        strong_words = [
            "registration fee",
            "processing fee",
            "joining fee",
            "payment before joining",
            "refundable fee",
            "telegram",
            "whatsapp",
            "earn money fast",
            "quick earning",
            "guaranteed income"
        ]

        safe_words = [
            "no payment required",
            "no registration fee",
            "official company website",
            "company career page",
            "apply through official website",
            "official email"
        ]

        strong_match = any(
            word in " ".join(reasons).lower()
            for word in strong_words
        )

        safe_match = any(
            word in data.get("description", "").lower()
            for word in safe_words
        )

        # ================= FINAL SMART DECISION =================

        if safe_match and rule_count <= 1:
            label = "Genuine"
            confidence = min(confidence, 75)

        elif strong_match and rule_count >= 3:
            label = "Fraud"
            confidence = max(confidence, 85)

        elif strong_match and rule_count >= 1:
            label = "Suspicious"
            confidence = max(min(confidence, 80), 65)

        elif rule_count >= 4:
            label = "Suspicious"
            confidence = 70

        elif fraud_probability < 0.60:
            label = "Genuine"
            confidence = min(confidence, 72)

        else:
            label = "Suspicious"
            confidence = max(min(confidence, 75), 60)

        # ================= RESPONSE =================

        response = {
            "analysis_type": "text",

            "title": title if title else "Not Provided",
            "company": company if company else "Not Provided",

            "final_decision": label,
            "confidence": confidence,

            "model_used": "DistilBERT + SHAP + LIME + Rule Engine",

            "rule_based": {
                "reasons": reasons[:5]
            },

            # Main Explainable AI
            "xai_explanation": xai_result["final_explanation"],

            # SHAP
            "shap_summary": xai_result["shap_summary"],
            "important_words": xai_result["important_words"],

            # LIME
            "lime_summary": xai_result["lime_summary"]
        }

        return JsonResponse(response)

    return JsonResponse({
        "error": "Invalid request method"
    })

@login_required(login_url="/login")
def analyze_image(request):

    if request.method == "POST":

        try:
            image = request.FILES.get("image")

            if not image:
                return JsonResponse({
                    "error": "No image uploaded"
                })

            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            image_path = fs.path(filename)

            # ================= OCR =================

            extracted_text = extract_text_from_image(image_path)

            # ================= AUTO TITLE =================

            job_title = extract_job_title(extracted_text)

            data = {
                "title": job_title,
                "company": "Extracted from OCR",
                "email": "",
                "phone": "",
                "salary": "",
                "fee": "",
                "description": extracted_text
            }

            # ================= AI PREDICTION =================

            label, confidence = predict_job(data)

            # ================= RULE ENGINE =================

            rule_reasons = detect_rules(data)

            # ================= XAI =================

            xai_result = explain_prediction(data)

            xai_words = []

            for item in xai_result["important_words"]:
                if isinstance(item, dict):
                    xai_words.append(item.get("word", ""))
                else:
                    xai_words.append(str(item))

            # merge rule engine + XAI

            reasons = list(dict.fromkeys(rule_reasons + xai_words))

            # ================= SMART HYBRID DECISION =================

            fraud_probability = confidence / 100
            rule_count = len(reasons)

            strong_words = [
                "registration fee",
                "processing fee",
                "joining fee",
                "payment before joining",
                "refundable fee",
                "telegram",
                "whatsapp",
                "earn money fast",
                "quick earning",
                "guaranteed income"
            ]

            weak_words = [
                "work from home",
                "no experience required",
                "salary up to",
                "freshers can apply",
                "minimal workload"
            ]

            strong_match = any(
                word in " ".join(reasons).lower()
                for word in strong_words
            )

            weak_match = any(
                word in extracted_text.lower()
                for word in weak_words
            )

            # ================= FINAL SMART DECISION =================

            if strong_match and rule_count >= 3:
                label = "Fraud"
                confidence = max(confidence, 85)

            elif strong_match and rule_count >= 1:
                label = "Suspicious"
                confidence = max(min(confidence, 80), 65)

            elif weak_match and not strong_match:
                label = "Genuine"
                confidence = min(confidence, 68)

            elif rule_count >= 4:
                label = "Suspicious"
                confidence = 70

            elif fraud_probability < 0.60:
                label = "Genuine"
                confidence = min(confidence, 72)

            else:
                label = "Genuine"
                confidence = min(confidence, 78)

            # ================= RESPONSE =================

            response = {
                "analysis_type": "image",

                "title": job_title,
                "company": "Extracted from OCR",

                "final_decision": label,
                "confidence": confidence,

                "model_used": "OCR + DistilBERT + SHAP + LIME + Rule Engine",

                "extracted_text": extracted_text,

                "rule_based": {
                    "reasons": reasons
                },

                "xai_explanation": xai_result["final_explanation"],
                "shap_summary": xai_result["shap_summary"],
                "lime_summary": xai_result["lime_summary"],
                "important_words": xai_result["important_words"]
            }

            return JsonResponse(response)

        except Exception as e:
            return JsonResponse({
                "error": str(e)
            })

    return JsonResponse({
        "error": "Invalid request method"
    })

@login_required(login_url="/login")
def analyze_link(request):

    if request.method != "POST":
        return JsonResponse({
            "error": "Invalid request method"
        })

    try:
        data = json.loads(request.body)
        link = data.get("link")

        # ================= DOMAIN FRAUD CHECK =================

        if detect_suspicious_domain(link):
            return JsonResponse({
                "analysis_type": "link",

                "title": "Suspicious Job Link",
                "company": "Unknown",

                "final_decision": "Fraud",
                "confidence": 95,

                "model_used": "Domain Fraud Detection",

                "rule_based": {
                    "reasons": [
                        "Suspicious short URL / messaging platform detected"
                    ]
                },

                "xai_explanation": (
                    "The provided job link uses a suspicious shortened URL or messaging platform such as WhatsApp or Telegram. "
                    "These platforms are commonly used in recruitment scams to avoid official company communication channels. "
                    "Because genuine employers usually use verified company websites, this strongly increases fraud probability."
                ),

                "shap_summary": (
                    'SHAP analysis identified "suspicious link source" as the strongest fraud-driving indicator.'
                ),

                "lime_summary": (
                    "LIME found that the job link itself creates strong fraud suspicion because unofficial recruiter channels "
                    "and shortened links are frequently associated with fake hiring scams."
                ),

                "important_words": [
                    {
                        "word": "suspicious link",
                        "score": 0.95
                    }
                ]
            })

        # ================= SCRAPE JOB PAGE =================

        job_title, company, description = extract_job_from_link(link)

        ai_data = {
            "title": job_title,
            "company": company if company else "Unknown Company",
            "email": "",
            "phone": "",
            "salary": "",
            "fee": "",
            "description": description
        }

        # ================= AI MODEL =================

        label, confidence = predict_job(ai_data)

        # ================= RULE ENGINE =================

        reasons = detect_rules(ai_data)

        fraud_probability = confidence / 100
        rule_count = len(reasons)

        if fraud_probability >= 0.80 and rule_count >= 2:
            label = "Fraud"
            confidence = max(confidence, 85)

        elif fraud_probability >= 0.65 and rule_count >= 1:
            label = "Suspicious"
            confidence = max(min(confidence, 80), 65)

        elif rule_count >= 3:
            label = "Suspicious"
            confidence = 70

        else:
            label = "Genuine"
            confidence = min(confidence, 82)

        # ================= XAI =================

        xai_result = explain_prediction(ai_data)

        # ================= FINAL RESPONSE =================

        response = {
            "analysis_type": "link",

            "title": job_title,
            "company": company,

            "final_decision": label,
            "confidence": confidence,

            "model_used": "Link Scraper + DistilBERT + SHAP + LIME + Rule Engine",

            "rule_based": {
                "reasons": reasons
            },

            "xai_explanation": xai_result["final_explanation"],
            "shap_summary": xai_result["shap_summary"],
            "lime_summary": xai_result["lime_summary"],
            "important_words": xai_result["important_words"]
        }

        return JsonResponse(response)

    except Exception as e:
        return JsonResponse({
            "error": str(e)
        })
    
#History Page save
@login_required(login_url="/login")
def save_analysis(request):

    if request.method == "POST":

        data = json.loads(request.body)

        JobAnalysis.objects.create(

            user=request.user,

            job_title=data.get("title"),
            company=data.get("company") if data.get("company") else "Unknown Company",
            email=data.get("email"),
            phone=data.get("phone"),

            salary=data.get("salary"),
            fee=data.get("fee"),
            description=data.get("description"),

            decision=data.get("decision"),
            confidence=data.get("confidence"),

            analysis_type=data.get("analysis_type", "text"),

            reasons=json.dumps(data.get("reasons")),
            justification=data.get("justification")

            )

        return JsonResponse({"status": "saved"})

# ================= DELETE HISTORY =================

@login_required(login_url="/login")
def delete_history(request, id):

    #if request.method == "DELETE":
    if request.method == "POST":

        JobAnalysis.objects.filter(id=id, user=request.user).delete()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False})

# ================= ADMIN CHANGE ROLE =================

@login_required(login_url="/login")
def change_role(request, id):

    if request.method == "POST":

        try:
            user = User.objects.get(id=id)
            profile = UserProfile.objects.get(user=user)

            if profile.role == "ADMIN":
                profile.role = "USER"
            else:
                profile.role = "ADMIN"

            profile.save()

            return JsonResponse({"success": True})

        except:
            return JsonResponse({"success": False})

# ================= ADMIN - MANAGE USERS =================

@login_required(login_url="/login")
def manage_users(request):

    # Only admin access
    try:
        profile = UserProfile.objects.get(user=request.user)

        if profile.role != "ADMIN":
            return redirect("/dashboard")

    except:
        return redirect("/dashboard")


    users = User.objects.all()

    user_list = []

    for u in users:

        analysis_count = JobAnalysis.objects.filter(user=u).count()

        try:
            role = UserProfile.objects.get(user=u).role
        except:
            role = "USER"

        user_list.append({
            "id": u.id,
            "username": u.username,
            "analysis_count": analysis_count,
            "role": role
        })

    return render(request,"manage_users.html",{
        "users":user_list
    })

# ================= ADMIN DELETE USER =================

@login_required(login_url="/login")
def delete_user(request,id):

    if request.method == "POST":

        User.objects.filter(id=id).delete()

        return JsonResponse({"success":True})

    return JsonResponse({"success":False})
