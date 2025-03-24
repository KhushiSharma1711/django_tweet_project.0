document.addEventListener("DOMContentLoaded", () => {
  // Like button functionality
  document.querySelectorAll(".like-btn").forEach((button) => {
    button.addEventListener("click", function () {
      const tweetId = this.getAttribute("data-tweet-id")
      fetch(`/tweet/${tweetId}/like/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          // Update like count
          document.querySelector(`#like-count-${tweetId}`).textContent = data.total_likes

          // Update dislike count
          document.querySelector(`#dislike-count-${tweetId}`).textContent = data.total_dislikes

          // Toggle liked class
          if (data.liked) {
            this.classList.add("liked")
            document.querySelector(`.dislike-btn[data-tweet-id="${tweetId}"]`).classList.remove("disliked")
          } else {
            this.classList.remove("liked")
          }
        })
        .catch((error) => {
          console.error("Error:", error)
        })
    })
  })

  // Dislike button functionality
  document.querySelectorAll(".dislike-btn").forEach((button) => {
    button.addEventListener("click", function () {
      const tweetId = this.getAttribute("data-tweet-id")
      fetch(`/tweet/${tweetId}/dislike/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          // Update like count
          document.querySelector(`#like-count-${tweetId}`).textContent = data.total_likes

          // Update dislike count
          document.querySelector(`#dislike-count-${tweetId}`).textContent = data.total_dislikes

          // Toggle disliked class
          if (data.disliked) {
            this.classList.add("disliked")
            document.querySelector(`.like-btn[data-tweet-id="${tweetId}"]`).classList.remove("liked")
          } else {
            this.classList.remove("disliked")
          }
        })
        .catch((error) => {
          console.error("Error:", error)
        })
    })
  })

  // Comment button functionality
  document.querySelectorAll(".comment-button").forEach((button) => {
    button.addEventListener("click", function () {
      const tweetId = this.getAttribute("data-tweet-id")
      const commentsSection = document.querySelector(`#comments-section-${tweetId}`)

      // Toggle comments section visibility
      if (commentsSection.classList.contains("comment-section-hidden")) {
        commentsSection.classList.remove("comment-section-hidden")
        loadComments(tweetId)
      } else {
        commentsSection.classList.add("comment-section-hidden")
      }
    })
  })

  // Function to load comments
  function loadComments(tweetId) {
    const commentsContainer = document.querySelector(`#comments-container-${tweetId}`)

    // Show loading spinner
    commentsContainer.innerHTML =
      '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i> Loading comments...</div>'

    fetch(`/tweet/${tweetId}/comments/`, {
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // Build comments HTML
          let commentsHTML = ""

          if (data.comments.length === 0) {
            commentsHTML = '<div class="text-center text-muted my-3">No comments yet. Be the first to comment!</div>'
          } else {
            data.comments.forEach((comment) => {
              commentsHTML += `
                <div class="comment-container">
                  <div class="comment-header">
                    <div class="comment-user">
                      <i class="fas fa-user-circle"></i> @${comment.username}
                    </div>
                    <div class="comment-time">
                      <i class="far fa-clock"></i> ${comment.created_at}
                    </div>
                  </div>
                  <div class="comment-content">
                    ${comment.content}
                  </div>
                </div>
              `
            })
          }

          commentsContainer.innerHTML = commentsHTML
        } else {
          commentsContainer.innerHTML = '<div class="alert alert-danger">Error loading comments</div>'
        }
      })
      .catch((error) => {
        console.error("Error:", error)
        commentsContainer.innerHTML = '<div class="alert alert-danger">Error loading comments</div>'
      })
  }

  // Handle comment form submissions
  document.querySelectorAll(".comment-submit-form").forEach((form) => {
    form.addEventListener("submit", function (e) {
      e.preventDefault()

      const tweetId = this.getAttribute("data-tweet-id")
      const contentInput = this.querySelector('textarea[name="content"]')
      const content = contentInput.value.trim()

      if (!content) return

      const formData = new FormData()
      formData.append("content", content)

      fetch(`/tweet/${tweetId}/comment/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "X-Requested-With": "XMLHttpRequest",
        },
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            // Clear input
            contentInput.value = ""

            // Reload comments
            loadComments(tweetId)

            // Update comment count
            const commentCount = document.querySelector(`#comment-count-${tweetId}`)
            commentCount.textContent = Number.parseInt(commentCount.textContent) + 1
          } else {
            alert("Error: " + (data.error || "Could not add comment"))
          }
        })
        .catch((error) => {
          console.error("Error:", error)
          alert("Error adding comment")
        })
    })
  })

  // Image upload preview
  const imageInput = document.getElementById("id_img")
  if (imageInput) {
    imageInput.addEventListener("change", function () {
      previewMedia(this, "image-preview", "image-filename")
    })
  }

  // Video upload preview
  const videoInput = document.getElementById("id_video")
  if (videoInput) {
    videoInput.addEventListener("change", function () {
      previewMedia(this, "video-preview", "video-filename")
    })
  }

  function previewMedia(input, previewId, filenameId) {
    const preview = document.getElementById(previewId)
    const filename = document.getElementById(filenameId)
    const previewContainer = document.querySelector(".media-preview")

    if (input.files && input.files[0]) {
      const reader = new FileReader()

      reader.onload = (e) => {
        preview.src = e.target.result
        filename.textContent = input.files[0].name
        previewContainer.style.display = "block"
      }

      reader.readAsDataURL(input.files[0])
    }
  }

  // Function to get CSRF token
  function getCookie(name) {
    let cookieValue = null
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";")
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim()
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
          break
        }
      }
    }
    return cookieValue
  }
})

