"""Media & hype views: power rankings and live tournament feed."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import HighlightForm, PowerRankingArticleForm
from .models import Highlight, PowerRankingArticle, Team


# ── Power Rankings ───────────────────────────────────────────────────────────

def rankings_list_view(request):
    """Public list of published power-ranking articles."""
    articles = PowerRankingArticle.objects.filter(
        is_published=True, publish_date__lte=timezone.now()
    ).order_by("-publish_date")
    return render(request, "tournament/rankings_list.html", {"articles": articles})


def ranking_detail_view(request, article_id):
    article = get_object_or_404(
        PowerRankingArticle,
        pk=article_id,
        is_published=True,
    )
    return render(request, "tournament/ranking_detail.html", {"article": article})


@login_required
def ranking_create_view(request):
    if not request.user.is_staff:
        return render(request, "tournament/403.html", status=403)
    if request.method == "POST":
        form = PowerRankingArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, "Ranking article published.")
            return redirect("platform:ranking_detail", article_id=article.id)
    else:
        form = PowerRankingArticleForm()
    return render(request, "tournament/ranking_form.html", {"form": form})


# ── Live Feed ────────────────────────────────────────────────────────────────

def live_feed_view(request):
    """TikTok/Twitter-style vertical feed of highlights, newest first."""
    highlights = Highlight.objects.select_related("team", "created_by").order_by("-created_at")
    return render(request, "tournament/live_feed.html", {"highlights": highlights})


@login_required
def highlight_submit_view(request):
    if request.method == "POST":
        form = HighlightForm(request.POST)
        if form.is_valid():
            highlight = form.save(commit=False)
            highlight.created_by = request.user
            highlight.save()
            messages.success(request, "Highlight submitted to the live feed.")
            return redirect("platform:live_feed")
    else:
        form = HighlightForm()
    return render(request, "tournament/highlight_submit.html", {"form": form})
