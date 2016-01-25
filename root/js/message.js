$('#sUserForm').submit(function(evt) {
    evt.preventDefault();
    $.ajax({
        url:'/api/message/send',
        type:'POST',
        data:{
            body:document.getElementsByName('body')[0].value,
            id:document.getElementsByName('id')[0].value
        },
        dataType:'json',
        success:function(data) {
            if ('error' in data) {
                $('#alert')[0].className="alert alert-danger";
                $('#alert').html(data.error);
            } else if ('success' in data) {
                $('#alert')[0].className="alert alert-success";
                $('#alert').html('Message sent!');
                document.getElementsByName('body')[0].value='';
                document.getElementsByName('body')[0].innerHTML='';
            }
        },
        error:function(data) {
            $('#alert')[0].className="alert alert-danger";
            $('#alert').text("Something went wrong...");
        }
    });
});

$('#gUserForm').submit(function(evt) {
    evt.preventDefault();
    $.ajax({
        url:'/api/message/send',
        type:'POST',
        data:{
            body:document.getElementsByName('body')[0].value,
            name:document.getElementsByName('name')[0].value
        },
        dataType:'json',
        success:function(data) {
            if ('error' in data) {
                $('#alert')[0].className="alert alert-danger";
                $('#alert').html(data.error);
            } else if ('success' in data) {
                $('#alert')[0].className="alert alert-success";
                $('#alert').html('Message sent!');
                document.getElementsByName('body')[0].value='';
                document.getElementsByName('body')[0].innerHTML='';
            }
        },
        error:function(data) {
            $('#alert')[0].className="alert alert-danger";
            $('#alert').text("Something went wrong...");
        }
    });
});