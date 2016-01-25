$('.vote').click(function() {
    var active = this.classList.contains('active');
    var isCom = this.classList.contains('comment');
    var isUp = this.classList.contains('upvote');

    var elm = this;
    var way = active?0:(isUp?1:-1);
    $.post(isCom? '/api/post/comment/vote' : '/api/post/vote',{
        'id':isCom? this.dataset.commentId : this.dataset.postId,
        'way':way
    }, function(data) {
        if ('success' in data) {
            if (active)
                elm.className = elm.className.replace(/\bactive\b/,'');
            else
                elm.className = elm.className+' active';

            var other = $(elm.parentNode).children(isUp?'.downvote':'.upvote')[0];
            var wasOp = other.classList.contains('active');
            other.className = other.className.replace(/\bactive\b/,'');

            var pe = $(elm.parentNode).children('.points')[0];
            var cv = parseInt(pe.innerHTML);
            pe.innerHTML = cv+(active?-1:1)*(wasOp?2:1)*(isUp?1:-1);
        }
    }, 'json');
});