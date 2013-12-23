/**
For all other js things on the dashbard
**/

$(function() {
    $(window).scroll(function() {
        var scroll = $(window).scrollTop();
        if (scroll >= 200) {
            $("#details").addClass("stickit");
        } else {
            $("#details").removeClass("stickit");
        }
    });
});