// Global Variables
var error_icon =
  `<div class="v-center"><div class="h-center"><img src="../static/images/red.png" style="height:100px;"></div></div>`;
var loading_icon =
  `<div class="v-center"><div class="h-center"><i class="fa fa-spinner fa-spin fa-4x"></i></div></div>`;
var loading_icon_4x =
  `<div class="v-center"><div class="h-center"><i class="fa fa-spinner fa-spin fa-4x"></i></div></div>`;
var loading_icon_1x =
  '<div class="h-center"><i class="fa fa-spinner fa-spin fa-1x"></i></div>';

// on WindowLoad functions
$(document).ready(function(){
  // Preloaded icons
  $('#preloaded_icons').html(loading_icon_1x + loading_icon_4x + error_icon);
});

// Render AJAX status icon
function display_status(target_el, status, message) {
  var icon_name = '';
  if (status=='loading') {
    icon_name = '<i class="fa fa-spinner fa-spin fa-5x"></i>';  
  }
  else if (status=='success') {
    icon_name = '<img src="../static/images/done.gif" class="img-fluid h-center" style="height: 120px;">';
  }
  else {
    icon_name = '<img src="../static/images/red.png" class="img-fluid h-center" style="height: 120px;">';
  }
  $(`#${target_el}`).html(`<div style="height:400px;" class="v-center"><div class="h-center">${icon_name}</div><div class="h-center my-5"><p class="text-center">${message}</p></div></div>`)
}

// Enable or disable an element
function enable_button(dom_id, button_class) {
  $(`#${dom_id}`).attr("disabled", false);
  $(`#${dom_id}`).removeClass("btn-outline-dark pointer_disabled").addClass(`"${button_class} pointer"`);
};
function disable_button(dom_id, button_class) {
  $(`#${dom_id}`).attr("disabled", true);
  $(`#${dom_id}`).removeClass(`"${button_class} pointer"`).addClass("btn-outline-dark pointer_disabled");
};


// // Create a click event listener for button btn_rewrite
// $('#btn_rewrite').click(function() {
//   run_genai();
//   disable_button('btn_rewrite');
// });


// Triger streaming func with async/await 
$('#btn_rewrite').click(async function (event) {
  event.preventDefault();
  run_genai_streaming();
  disable_button('btn_rewrite');
});

// Function to add text into textarea field
function insert_context(text) {
  $('#context').val(text);
}

// Function to reload page
function reload_page() {
  location.reload();
}

// Function to clear text from textarea field
function clear_text_field(element_id) {
  var el = document.getElementById(element_id);
  el.value = '';
}

// Function to copy text from textarea field into clipboard
function copy_to_clipboard(element_id) {
  var copyText = document.getElementById(element_id);
  copyText.select();
  copyText.setSelectionRange(0, 99999);
  document.execCommand("copy");
}

// Non-streaming async call
function run_genai(){
  // Adding input field data as JSON
  var form_data = JSON.stringify({
    context: $('#context').val(),
    draft_writing: $('#draft_writing').val(),
    tone_style: $('#tone_style').find(":selected").val(),
    language: $('#language').find(":selected").val(),
    advanced_vocabulary: $('input[name=advanced_vocabulary]:checked').val(),
    allow_feedback: $('input[name=allow_feedback]:checked').val(),
    use_gpt4: $('input[name=use_gpt4]:checked').val(),
    active_feedback: $('#active_feedback').val(),
    assistant_writing: $('#assistant_writing').val(),
  });
  $.ajax({
    url: $SCRIPT_ROOT + '/run',
    type: 'POST',
    data: form_data,
    contentType: 'application/json;charset=UTF-8',
    dataType: 'json',
    processData: false,
    beforeSend: function() {
      $('#div_loading').html(loading_icon);
    }
  }).done(function(response) {
    enable_button('btn_rewrite');
    if (response.status=='error') {
      $('#div_loading').html(
        error_icon + `<div class="text-center h-center pt-3 text-s" style="color: red;"><p>${response.message}</p></div>`
        );
    }
    else { 
      $('.assistant_writing').html(response.output);
      $('#div_loading').html('');

      if ($('input[name=allow_feedback]:checked').val()=="on") {
        $('#div_active_feedback').show();
      }
    } 
  });
}

// Chunk sentence into array of fixed blocked size for better streaming UX
function chunkSentence(sentence, blockLength) {
  const blocks = [];
  for (let i = 0; i < sentence.length; i+=blockLength) {
    blocks.push(sentence.slice(i, i+blockLength));
  }
  return blocks;
}

// Streaming async call
async function run_genai_streaming(){
  
  var formData = new FormData();
  formData.append('context',  $('#context').val());
  formData.append('draft_writing',  $('#draft_writing').val());
  formData.append('tone_style',  $('#tone_style').find(":selected").val());
  formData.append('language',  $('#language').find(":selected").val());
  formData.append('advanced_vocabulary',  $('input[name=advanced_vocabulary]:checked').val());
  formData.append('allow_feedback',  $('input[name=allow_feedback]:checked').val());
  formData.append('use_gpt4',  $('input[name=use_gpt4]:checked').val());
  formData.append('active_feedback',  $('#active_feedback').val());
  formData.append('assistant_writing',  $('#assistant_writing').val()); 

  console.log($('#language').find(":selected").val());
  console.log('Advanced Vocabulary:' + $('input[name=advanced_vocabulary]:checked').val());
  console.log('Use GPT4:' + $('input[name=use_gpt4]:checked').val());

  // pre-process UI elements
  $('#div_loading').html(loading_icon);
  document.getElementById("assistant_writing").innerHTML = "";
  document.getElementsByClassName("assistant_writing")[1].innerHTML = "";
  
  try {
      const response = await fetch('/run', {
          method: 'POST',
          body: formData
      });
      const reader = response.body.getReader();
      while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          // Split sentences into bite-sized chunks for improved UI rendering
          const text = new TextDecoder().decode(value);
          const words = chunkSentence(text, 5);
          for (const word of words) {
              document.getElementById("assistant_writing").innerHTML += word;
              document.getElementsByClassName("assistant_writing")[1].innerHTML += word;
          }
          await new Promise(resolve => setTimeout(resolve, 10));
      }
      // post-process UI elements 
      enable_button('btn_rewrite');
      $('#div_loading').html('');
      if ($('input[name=allow_feedback]:checked').val()=="on") {
        $('#div_active_feedback').show();
      }
  } catch (error) {
      console.error(error);
  }
}


// Add a click event on button btn_tc
$('#btn_tc').click(function() {
  $('#div_tc').toggle();
})


// Add a click event listener on button btn_register
$('#btn_register').click(function(e) {
  // Prevent the default button click behavior
  e.preventDefault();

  // Validate the form inputs
  const form = $('#form_register').get(0);
  if (!form.checkValidity()) {
    form.classList.add("was-validated");
    return;
  }

  var form_data = JSON.stringify({
    email: $('#email').val(),
    password: $('#pwd').val(),
    first_name: $('#firstname').val(),
    last_name: $('#lastname').val()
  });
  $.ajax({
    url: $SCRIPT_ROOT + '/register_ajax',
    type: 'POST',
    data: form_data,
    contentType: 'application/json;charset=UTF-8',
    dataType: 'json',
    processData: false,
    beforeSend: function() {
      $('#btn_register').html(loading_icon_1x);
      disable_button('btn_register', 'btn-primary');
    }
  }).done(function(response) {
    if (response.status=='error') {
      $('#div_register').html(
        error_icon + `<span class="text-center h-center pt-3 text-s" style="color: red;"><p>${response.message}</p></span>`
        );
      enable_button('btn_register', 'btn-primary');
      $('#btn_signin').html('Register');
    }
    else { 
      $('#div_register').html(
        `<div class="small h-center text-center"><i class="bi bi-check-circle mx-2"></i> Account successfully created<br>Signing you in...</div>`
        );
      // Redirect to login page after 1 second
      setInterval(function(){ window.location.replace("/login"); }, 3000);
    } 
  })
})


// Add a click event listener on button btn_signin
$('#btn_signin').click(function(e) {
  // Prevent the default button click behavior
  e.preventDefault();

  // Validate the form inputs
  const form = $('#form_login').get(0);
  if (!form.checkValidity()) {
    form.classList.add("was-validated");
    return;
  }

  var form_data = JSON.stringify({
    email: $('#email').val(),
    password: $('#pwd').val()
  });
  $.ajax({
    url: $SCRIPT_ROOT + '/auth',
    type: 'POST',
    data: form_data,
    contentType: 'application/json;charset=UTF-8',
    dataType: 'json',
    processData: false,
    beforeSend: function() {
      $('#btn_signin').html(loading_icon_1x);
      disable_button('btn_signin', 'btn-primary');
    }
  }).done(function(response) {
    if (response.status=='error') {
      $('#div_login_error').html(
        `<div class="my-2 text-center"><code>Invalid username or password</code></div>`
        );
      enable_button('btn_signin', 'btn-primary');
      $('#btn_signin').html('Login');
    }
    else {
      // Redirect to login page after 1 second
      setInterval(function(){ window.location.replace("/"); }, 1000);
    } 
  })
})