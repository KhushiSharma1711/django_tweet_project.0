from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import UserTweetForm
from .models import Tweet, Comment
from django import forms
import os

# Tweet form class
class TweetForm(forms.ModelForm):
    img_url = forms.URLField(required=False, label="Image URL (optional)",
                         widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Paste image URL here'}),
                         max_length=2000)
  
    class Meta:
        model = Tweet
        fields = ['content', 'img_url', 'img', 'video']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What\'s happening?'}),
            'img': forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'image/*', 'id': 'id_img'}),
            'video': forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'video/*', 'id': 'id_video'}),
        }

# Comment form class
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Write a comment...'}),
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
    comment_form = CommentForm()
    return render(request, 'tweet_list.html', {'tweets': tweets, 'comment_form': comment_form})

@login_required
def tweet_detail(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    comments = tweet.comments.all()
    comment_form = CommentForm()
    
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.tweet = tweet
            comment.user = request.user
            comment.save()
            return redirect('tweet_detail', pk=pk)
            
    return render(request, 'tweet_detail.html', {
        'tweet': tweet, 
        'comments': comments,
        'comment_form': comment_form
    })

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
            
            # Clear image if URL is provided and different from current
            if form.cleaned_data.get('img_url') and tweet.img and form.cleaned_data.get('img_url') != tweet.img_url:
                # Delete the old image file
                if os.path.isfile(tweet.img.path):
                    os.remove(tweet.img.path)
                tweet.img = None
                
            # If new image is uploaded, remove the URL
            if form.cleaned_data.get('img') and tweet.img_url:
                tweet.img_url = None
                
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
        # The delete method in the model will handle media deletion
        tweet.delete()
        return redirect('tweet_list')
    return render(request, 'delete.html', {'tweet': tweet})

@login_required
def like_tweet(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    
    # Check if the request is AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.user in tweet.likes.all():
        tweet.likes.remove(request.user)
        liked = False
    else:
        tweet.likes.add(request.user)
        liked = True
        # Remove dislike if exists
        if request.user in tweet.dislikes.all():
            tweet.dislikes.remove(request.user)
    
    response_data = {
        'liked': liked,
        'total_likes': tweet.total_likes(),
        'total_dislikes': tweet.total_dislikes()
    }
    
    if is_ajax:
        return JsonResponse(response_data)
    else:
        # For non-AJAX requests, redirect back to the page
        return redirect('tweet_detail', pk=pk)

@login_required
def dislike_tweet(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    
    # Check if the request is AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.user in tweet.dislikes.all():
        tweet.dislikes.remove(request.user)
        disliked = False
    else:
        tweet.dislikes.add(request.user)
        disliked = True
        # Remove like if exists
        if request.user in tweet.likes.all():
            tweet.likes.remove(request.user)
    
    response_data = {
        'disliked': disliked,
        'total_likes': tweet.total_likes(),
        'total_dislikes': tweet.total_dislikes()
    }
    
    if is_ajax:
        return JsonResponse(response_data)
    else:
        # For non-AJAX requests, redirect back to the page
        return redirect('tweet_detail', pk=pk)

@login_required
def add_comment(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    
    if request.method == "POST":
        content = request.POST.get('content', '').strip()
        if content:
            comment = Comment.objects.create(
                tweet=tweet,
                user=request.user,
                content=content
            )
            
            # Return JSON for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'comment_id': comment.id,
                    'username': comment.user.username,
                    'content': comment.content,
                    'created_at': comment.created_at.strftime("%b %d, %Y, %I:%M %p"),
                    'total_comments': tweet.comments.count()
                })
        
        # Return error for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Comment cannot be empty'})
            
    return redirect('tweet_detail', pk=pk)

@login_required
def get_comments(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    comments = tweet.comments.all()
    
    comments_data = []
    for comment in comments:
        comments_data.append({
            'id': comment.id,
            'username': comment.user.username,
            'content': comment.content,
            'created_at': comment.created_at.strftime("%b %d, %Y, %I:%M %p"),
            'is_owner': comment.user == request.user
        })
    
    return JsonResponse({
        'success': True,
        'comments': comments_data,
        'total_comments': len(comments_data)
    })

