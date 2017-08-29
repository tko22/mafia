$(function(){
    //csrf stuff
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
    });

    var toggle_state = 0 //showing
    $('.toggle-show-role').click(function(){
        if (toggle_state == 0) {
            $('.role-text-container').hide();
            toggle_state = 1;

        }
         else{
            $('.role-text-container').show();
            toggle_state=0;
         }
    });


    $("body").on("click",".users-ingame",function(){
        $(this).toggleClass("users-ingame users-ingame-striked");
    });
    $("body").on("click",".users-ingame-striked",function(){
        $(this).toggleClass("users-ingame-striked users-ingame");
    });

    $('#leave-btn').click(function(){
        $.ajax({
            type:'POST',
            url: '/api/leavegame',
            data:JSON.stringify({
                name: $('.center').attr('id'),
                code: $('body').attr('class'),
            }),
            dataType: 'json',
            success: function(data){
                if (data.status == 'failed'){
                    alert(data.message);
                    window.location.replace("/");
                }
                else{
                    window.location.replace("/");
                }
            }


        })

    });

    $('#end-btn').click(function(){
        $.ajax({
            type:'POST',
            url: '/api/endround',
            data:JSON.stringify({
                name: $('.center').attr('id'),
                code: $('body').attr('class'),
            }),
            dataType: 'json',
            success: function(data){
                if (data.status == 'failed'){
                    alert(data.message);
                    window.location.replace("/");
                }
                else{
                    window.location.replace("/"+data.code);
                }
            }


        })


    });

    $('#start-round-btn').click(function(){
        $.ajax({
            type:'POST',
            url: '/api/startround',
            data: JSON.stringify({
                code : $('body').attr('class'),
            }),
            dataType: 'json',
            success: function(data){
                $('.round').text(data.round);
            }

        })
    });
    getRound();
});
var interval;
function startTimer(duration) {
    var timer = duration, minutes, seconds;
    clearInterval(interval);
    interval = setInterval(function () {
        minutes = parseInt(timer / 60, 10)
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        $('.counter').text(minutes + ":" + seconds);

        if (--timer < 0) {
            stopTimer();
        }
    }, 1000);
}
function stopTimer(){
    clearInterval(interval);

}
var duration = 60;
var round_number = 0;
function getRound(){
    $.ajax({
        type:'POST',
        url: '/api/getround',
        data:JSON.stringify({
            name: $('.center').attr('id'),
            code: $('body').attr('class'),
        }),
        contentType: "application/json",
        success: function(data){
            if (data.in_game == false){
                window.location.replace("/"+data.code);
            }
            $('.round').text(data.round)
            duration = data.round_len * 60
            if (round_number.toString() != data.round){
                console.log(round_number);
                round_number = data.round;

                startTimer(duration);
            }


        }
    })
    setTimeout(getRound,3000);

}

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