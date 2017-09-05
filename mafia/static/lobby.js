var num_users=0;
var users = [];
var first = 0;
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



    $('.remove-btn').click(function(){
        $(this).closest('.user-entry').remove();
        $.ajax({
            type:'POST',
            url: '/api/removeuser',
            data: JSON.stringify({
                name: $(this).attr('id'),
                code: $('#game-code').attr('class'),
            }),
            dataType: 'json',
            success: function(data){
            }
        })
    });



    $('#start-lobby-btn').click(function(event){
        var rt = parseInt($('#roundtime-form').val());
        var narrator = $('#narrator-form').val();
        var vampire = $('#vampire-form').is(':checked');
        var cop = $('#cop-form').is(':checked');
        console.log('start game');
        $.ajax({
            type:'POST',
            url:'/api/startgame',
            data: JSON.stringify({
                code: $('#game-code').attr('class'),
                vampire: vampire,
                time: rt,
                narrator: narrator,
                cop: cop,
            }),

            dataType:'json',
            success: function(data){
                if(data.status == "success"){
                    window.location.replace("/"+data.code+"/game");
                }
                else{
                    console.log(data.message);
                    $('#error-msg').text(data.message);
                    $('#error-msg').show()
                }
            }


        })
    });

    //leave lobby
    $('#leave-btn').click(function(event){
        $.ajax({
            type:'POST',
            url: '/api/leavelobby',
            data:JSON.stringify({
                name: $('.center').attr('id'),
                code: $('#game-code').attr('class'),
            }),
            dataType: 'json',
            success: function(data){
                window.location.replace("/");
            }
        })
        window.location.replace("/");
    });
    getusers();

});




Array.prototype.diff = function(a) {
    return this.filter(function(i) {
        return a.indexOf(i) < 0;
    });
};

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


function getusers(){
    $.ajax({
            type:'POST',
            url: '/api/getusers',
            data: JSON.stringify({
                code: $('#game-code').attr('class'),
            }),
            async: true,
            dataType: 'json',
            success: function(data){
                if (data.status == "failed" ) {
                    if ( data.message == "your user has been deleted"){
                        window.location.replace("/");
                    }
                }
                if (data.in_game == true){
                    window.location.replace("/"+data.code+"/game/")
                    return;
                }
                if (data.users.length != num_users){

                    var diffar = users.diff(data.users);
                    if (first == 0){
                        users = data.users;
                        first = 1;
                        return;
                    }
                    if (diffar.length == 0 ){
                        var diffar = data.users.diff(users);
                    }

                    //user removed
                    if (data.users.length < num_users && diffar.length > 0){
                        console.log('remove');
                        var x;
                        for (x=0;x<diffar.length;++x) {
                            $('#'+diffar[x]+'-div').remove();
                            $('.f-'+diffar[x]).remove();
                        }
                    }
                    //user added
                    else if(data.users.length > num_users && diffar.length > 0){
                       console.log('add');
                       var x;
                       for (x=0;x<diffar.length;++x) {
                            var b = $("<div class='user-entry' id="+diffar[x]+"-div></div>");
                            b.append("<p class='user-name'>"+diffar[x]+"</p>");
                            b.append("<span class='glyphicon glyphicon-remove remove-btn' id="+diffar[x]+" aria-hidden='true'></span>");
                            $('.userlistform').append(b);
                            var c = $("<option class='f-"+diffar[x]+"'>"+diffar[x]+"</option>");
                            $("#narrator-form").append(c);

                       }
                    }
                }

                users = data.users;
                num_users= data.users.length;


            }
    });
    setTimeout(getusers, 2000);

}