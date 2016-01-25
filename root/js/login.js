$('#loginForm').submit(function(evt) {
    evt.preventDefault();
    $.ajax({
        url:'/api/login/',
        type:'POST',
        data:{
            name:document.getElementsByName('name')[0].value,
            pass:document.getElementsByName('pass')[0].value
        },
        dataType:'json',
        success:function(data) {
            console.log(data);
            if ('error' in data) {
                $('#alert')[0].className="alert alert-danger";
                $('#alert').text(data.error);
            } else if ('success' in data) {
                document.location='/';
            }

        },
        error:function(data) {
            $('#alert')[0].className="alert alert-danger";
            $('#alert').text("Something went wrong...");
        }
    });
});

$('#registerForm').submit(function(evt) {
    evt.preventDefault();
    $.ajax({
        url:'/api/register/',
        type:'POST',
        data:{
            name:document.getElementsByName('name')[0].value,
            pass:document.getElementsByName('pass')[0].value,
            passCom:document.getElementsByName('passCom')[0].value,
        },
        dataType:'json',
        success:function(data) {
            console.log(data);
            if ('error' in data) {
                $('#alert')[0].className="alert alert-danger";
                $('#alert').text(data.error);
            } else if ('success' in data) {
                document.location='/login?reg=true';
            }

        },
        error:function(data) {
            $('#alert')[0].className="alert alert-danger";
            $('#alert').text("Something went wrong...");
        }
    });
});