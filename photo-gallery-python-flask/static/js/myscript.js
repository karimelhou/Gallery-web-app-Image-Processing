/***************************** Authentication Actions  ******************************/
$("#loginbtn").on("click", function(){
  var user = $("#loginUsername").val();
  var password = $("#loginPassword").val();
  var nextURL = $("#nextURL").val();

  $("#loginLoader").html('<img src="/static/images/loader.gif">');

  $.post("/login", {username: user, password: password}, function (response) {
    $("#loginLoader").html('');
    var response = JSON.parse(response);

    if (response.success) {
      alert("Login successful. User type: " + response.type);
      window.location.href = nextURL;
    }
    else {
       $("#loginLoader").html('<p class="alert alert-danger">Invalid username/password</p>');
    }
  });
});

$("#logoutbtn").on("click", function(){
  $.post("/logout", {action: 'logout'}, function (response) {
    window.location.href = "index.php";
  });
});

$("#registrationForm").on("submit", function(event){
  event.preventDefault();

  var username = $("#registerUsername").val();
  var password = $("#registerPassword").val();
  var userType = $("#registerType").val();

  $("#registrationLoader").html('<img src="/static/images/loader.gif">');

  $.post("/register", {username: username, password: password, type: userType}, function (response) {
      $("#registrationLoader").html('');
      var response = JSON.parse(response);

      if (response.result) {
          alert("Registration successful!");
      } else {
          alert("Registration failed: " + response.message);
      }
  });
});

// Functionality to toggle between login and registration forms
$("#showRegistrationForm").on("click", function(){
    $("#loginContainer").hide();
    $("#registrationContainer").show();
});

$("#showLoginForm").on("click", function(){
    $("#registrationContainer").hide();
    $("#loginContainer").show();
});



/***************************** Gallery Actions  ******************************/
// Add Gallery Action
$("#addGallerybtn").on("click", function(){
    var galleryName = $("#galleryName").val();

    if(galleryName != "") {
      $("#loader").html('<img src="/static/images/loader.gif">');

      $.when($.post("/galleries/add", {galleryName: galleryName}).done(function(response){
            $("#loader").html('');
            var response = JSON.parse(response);

            if (response.success) {
                location.reload();
            }
            else {
              console.log("Error Adding Gallery");
              location.reload();
            }
        }));
    }
});

// Delete Gallery Action
$(document).on("click", '.delete-gallery', function(){
  var galleryId = $(this).data("id");

  if(galleryId != "") {
    $("#loader").html('<img src="/static/images/loader.gif">');

    $.post("/galleries/delete", {galleryId: galleryId})
      .done(function(response){
          $("#loader").html('');
          var response = JSON.parse(response);

          if (response.success) {
              location.reload();
          }
          else {
            console.log("Error deleting Gallery");
          }
      });
  }
});

// Edit Gallery Modal Action
$("#editGalleryModalBtn").on("click", function(){
  var newGalleryName = $("#newGalleryName").val();
  var galleryId = $("#galleryId").val(); // We are using galleryId instead of old name

  if(newGalleryName != "" && galleryId != "") {
    $("#loader").html('<img src="/static/images/loader.gif">');

    $.post("/galleries/edit", {galleryId: galleryId, newName: newGalleryName})
      .done(function(response){
          $("#loader").html('');
          var response = JSON.parse(response);

          if (response.success) {
              location.reload();
          }
          else {
            console.log("Error renaming Gallery");
          }
      });
  }
});

// Additional JavaScript for Edit Button Click (Populating the Edit Modal)
$(document).on('click', '.edit-gallery', function() {
  var galleryId = $(this).data('id');
  var galleryName = $(this).data('name');

  // Set the data in the modal
  $('#galleryId').val(galleryId);
  $('#newGalleryName').val(galleryName);

  // Now, when the user clicks the 'edit' button on a gallery, the modal will pop up with the fields pre-filled.
});


/***************************** Photos Actions  ******************************/
// Delete Photo Action
$(document).on("click", '#deletePhotobtn', function() {
  var galleryName = $(this).data("galleryname");
  var photoName = $(this).data("photoname");
  var imgSrc = $(this).data("imgsrc"); // Get the image source

  if (galleryName !== "") {
      $.post("/galleries/album/photos/delete", { galleryName: galleryName, photoName: photoName, imgSrc: imgSrc }, function(response) {
      var response = JSON.parse(response);

          if (response.success) {
              location.reload();
          } else {
              console.log("Error Deleting Photo");
              location.reload();
          }
      });
  }
});



// When clicking on the image thumbnail
$(document).on("click", '#popImage', function() {
  var imgSrc = $(this).data("imgsrc");
  
  // Show the image in the modal
  $('#imagepreview').attr('src', imgSrc);
  $('#imagemodal').modal('show');  // show the image modal
});

// When clicking on the "Calculate" link
$(document).on("click", '.calculateImageProperties', function() {
  var $this = $(this); // Correctly reference 'this'
  var galleryName = $this.data("galleryname");
  var photoName = $this.data("photoname");

  // Start the calculation
  $.post("/galleries/album/" + galleryName + "/calculate/" + photoName, function(data) {
    if (data.success) {
      alert("Calculation was successful. You can now view the results.");
      // Update the 'Processed' indicator for this photo
      $this.closest('.thumb').find('.processed-indicator').text('Calculated');
    } else {
      alert("Failed to calculate properties: " + data.message);
    }
  }).fail(function(jqXHR, textStatus, errorThrown) {
    alert("Error in calculation request: " + errorThrown);
  });
});



// When clicking on the "View Results" link
$(document).on("click", '.viewImageProperties', function() {
  var galleryName = $(this).data("galleryname");
  var photoName = $(this).data("photoname");

  // Set the modal body with placeholders
  $('#plotmodal .modal-body').html(`
    <div id="processing_message" class="d-flex justify-content-center"><p>Processing, please wait...</p></div>
    <div id="color_moments_plot_container"></div>
    <div id="histograms_plot_container"></div>
    <div id="dominant_colors_container"></div>
  `);
  $('#plotmodal').modal('show');

  // Fetch and display the properties
  $.get("/galleries/album/" + galleryName + "/view_calculation/" + encodeURIComponent(photoName), function(data) {
    if (data.success) {
      // Remove the processing message
      $('#processing_message').remove();

      // Insert the plots into their respective containers
      $('#color_moments_plot_container').html(data.content.color_moments_plot);
      $('#histograms_plot_container').html(data.content.histograms_plot);

      // Map and insert dominant colors
      var dominantColorsHTML = data.content.dominant_colors.map(color => {
        var colorString = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
        return `<div style="background:${colorString}; width:60px; height:60px; display:inline-block; margin:5px;"></div>`;
      }).join("");
      $('#dominant_colors_container').html(dominantColorsHTML);
    } else {
      alert("Results not found. Please calculate first.");
      $('#plotmodal').modal('hide');
    }
  }).fail(function(jqXHR, textStatus, errorThrown) {
    console.error("Error in view request: " + errorThrown);
    $('#plotmodal').modal('hide');
  });
});











