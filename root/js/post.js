$('#postForm').submit(function(evt) {
    evt.preventDefault();
    $.ajax({
        url:'/api/post/submit',
        type:'POST',
        data:{
            title:document.getElementsByName('title')[0].value,
            body:document.getElementsByName('body')[0].value
        },
        dataType:'json',
        success:function(data) {
            if ('error' in data) {
                $('#alert')[0].className="alert alert-danger";
                $('#alert').html(data.error);
            } else if ('success' in data) {
                document.location='/post?id='+data.post;
            }

        },
        error:function(data) {
            $('#alert')[0].className="alert alert-danger";
            $('#alert').text("Something went wrong...");
        }
    });
});

$('#linkForm').submit(function(evt) {
    evt.preventDefault();
    $.ajax({
        url:'/api/post/link/submit',
        type:'POST',
        data:{
            title:document.getElementsByName('linktitle')[0].value,
            url:document.getElementsByName('url')[0].value
        },
        dataType:'json',
        success:function(data) {
            if ('error' in data) {
                $('#alertLink')[0].className="alert alert-danger";
                $('#alertLink').html(data.error);
            } else if ('success' in data) {
                $('#alertLink')[0].className="alert alert-success";
                $('#alertLink').html(data.info);
            }

        },
        error:function(data) {
            $('#alert')[0].className="alert alert-danger";
            $('#alert').text("Something went wrong...");
        }
    });
});

$('#commentForm').submit(function(evt) {
    evt.preventDefault();
    $.ajax({
        url:'/api/post/comment/add',
        type:'GET',
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
                document.location='/post?id='+data.post;
            }

        },
        error:function(data) {
            $('#alert')[0].className="alert alert-danger";
            $('#alert').text("Something went wrong...");
        }
    });
});

$('#shareForm').submit(function(evt) {
    evt.preventDefault();
    $.ajax({
        url:'/api/post/share',
        type:'POST',
        data:{
            postId:document.getElementsByName('postId')[0].value,
            username:document.getElementsByName('username')[0].value
        },
        dataType:'json',
        success:function(data) {
            if ('error' in data) {
                $('#shareAlert')[0].className="alert alert-danger";
                $('#shareAlert').html(data.error);
            } else if ('success' in data) {
                $('#shareAlert')[0].className="alert alert-success";
                $('#shareAlert').html("Shared post!");
            }

        },
        error:function(data) {
            $('#shareAlert')[0].className="alert alert-danger";
            $('#shareAlert').text("Something went wrong...");
        }
    });
});