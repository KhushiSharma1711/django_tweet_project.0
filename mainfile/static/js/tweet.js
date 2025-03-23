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
  
  