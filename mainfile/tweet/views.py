from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import UserTweetForm
from .models import Tweet
from django import forms

# Tweet form class
class TweetForm(forms.ModelForm):
    img_url = forms.URLField(required=False, label="Image URL (optional)",
                           widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Paste image URL here'}))
    
    class Meta:
        model = Tweet
        fields = ['content', 'img_url', 'img', 'video']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What\'s happening?'}),
            'img': forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'image/*'}),
            'video': forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'video/*'}),
        }

def register(request):
    if request.method == 'POST':
        form = UserTweetForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tweet_list')
    else:
        form = UserTweetForm()
    return render(request, 'register.html', {'form': form})

# Tweet views
def tweet_list(request):
    tweets = Tweet.objects.all().order_by('-created_at')
    return render(request, 'tweet_list.html', {'tweets': tweets})

@login_required
def tweet_detail(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    return render(request, 'tweet_detail.html', {'tweet': tweet})

@login_required
def tweet_new(request):
    if request.method == "POST":
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect('tweet_list')
    else:
        form = TweetForm()
    return render(request, 'tweet_form.html', {'form': form})

@login_required
def tweet_edit(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    if tweet.user != request.user:
        return redirect('tweet_list')
    
    if request.method == "POST":
        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.save()
            return redirect('tweet_list')
    else:
        form = TweetForm(instance=tweet)
    return render(request, 'tweet_form.html', {'form': form})

@login_required
def tweet_delete(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    if tweet.user != request.user:
        return redirect('tweet_list')
    
    if request.method == "POST":
        tweet.delete()
        return redirect('tweet_list')
    return render(request, 'delete.html', {'tweet': tweet})

@login_required
def like_tweet(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    if request.user in tweet.likes.all():
        tweet.likes.remove(request.user)
        liked = False
    else:
        tweet.likes.add(request.user)
        liked = True
        # Remove dislike if exists
        if request.user in tweet.dislikes.all():
            tweet.dislikes.remove(request.user)
    
    return JsonResponse({
        'liked': liked,
        'total_likes': tweet.total_likes(),
        'total_dislikes': tweet.total_dislikes()
    })

@login_required
def dislike_tweet(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    if request.user in tweet.dislikes.all():
        tweet.dislikes.remove(request.user)
        disliked = False
    else:
        tweet.dislikes.add(request.user)
        disliked = True
        # Remove like if exists
        if request.user in tweet.likes.all():
            tweet.likes.remove(request.user)
    
    return JsonResponse({
        'disliked': disliked,
        'total_likes': tweet.total_likes(),
        'total_dislikes': tweet.total_dislikes()
    })

