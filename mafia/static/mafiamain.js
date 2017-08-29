$(function() {

    //csrf stuff
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
    });

    $( "#start-btn" ).click(function( event ) {
        $('.main-menu').hide();
        $('#game-form').hide();
        $('.create-game').show();
        $('#create-btn').show();
        $('#join-btn-2').hide();
    });
    $( '#join-btn').click(function(event){
        $('.main-menu').hide();
        $('.create-game').show();
        $('#game-form').show();
        $('#join-btn-2').show();
        $('#create-btn').hide();
    });

    $( '#create-btn').click(function(event){
        var csrftoken = getCookie('csrftoken');
        $.ajax({
            type:'POST',
            url: '/api/createlobby',
            data: JSON.stringify({
                name:$('#name-form').val()}),
            dataType: "json",
            success: function(data){
                console.log(data.gamecode);
                window.location.replace("/"+data.gamecode);
            }
        })

    });

    //join btn when user clicks the Join Game btn in main menu
    $('#join-btn-2').click(function(event){
        var csrftoken = getCookie('csrftoken');
        $.ajax({
            type:'POST',
            url: '/api/joinlobby',
            data: JSON.stringify({
                name:$('#name-form').val(),
                code:$('#game-form').val()}),
            dataType: "json",
            success: function(data){
                if ( data.status === 'failed') {
                    $('#error-msg').text(data.message).show();
                }
                else{
                    window.location.replace("/"+data.gamecode);
                }

            }
        })
    });
    $( '#back-btn').click(function(event){
        $('.main-menu').show();
        $('.create-game').hide();
    });



});


//csrf stuff
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}