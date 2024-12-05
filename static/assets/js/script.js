// Fungsi untuk menampilkan preview gambar setelah dipilih
function previewImage() {
    const fileInput = document.getElementById('imageUpload');
    const imagePreview = document.getElementById('imagePreview');
    const file = fileInput.files[0];
  
    if (file) {
      const reader = new FileReader();
  
      reader.onload = function (e) {
        imagePreview.src = e.target.result;
        imagePreview.style.display = 'block';
      };
  
      reader.readAsDataURL(file);
    } else {
      imagePreview.style.display = 'none';
    }
  }
  
  // Fungsi untuk membuka kamera
  let stream;
  function openCamera() {
    document.getElementById("cameraContainer").style.display = "block";
    const video = document.getElementById("video");
  
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
      .then((mediaStream) => {
        stream = mediaStream;
        video.srcObject = mediaStream;
      })
      .catch((error) => {
        console.error("Error accessing camera: ", error);
      });
  }
  
  // Fungsi untuk menangkap gambar dari kamera
  function captureImage() {
    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    const capturedImage = document.getElementById("capturedImage");
  
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
  
    capturedImage.src = canvas.toDataURL("image/png");
    capturedImage.style.display = "block";
    document.getElementById("imageUpload").required = false;
  
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      video.srcObject = null;
    }
  
    document.getElementById("cameraContainer").style.display = "none";
  
    canvas.toBlob((blob) => {
      const fileInput = document.getElementById("imageUpload");
      const file = new File([blob], "captured_image.png", { type: "image/png" });
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      fileInput.files = dataTransfer.files;
    });
  }
  
  // Menambahkan efek saat scroll
  window.addEventListener('scroll', function () {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 10) {
      navbar.classList.add('navbar-scrolled');
    } else {
      navbar.classList.remove('navbar-scrolled');
    }
  });