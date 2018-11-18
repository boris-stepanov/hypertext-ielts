function spoiler(identifier) {
    prev = document.getElementById("sentenceChoose").prev;
    document.getElementById("sentenceChoose").prev=identifier;
    if (prev) {
        document.getElementById("block"+prev).style.display="none";
    };
    document.getElementById("block"+identifier).style.display="block";
    //    if (that.opened) {
    //        document.getElementById("block"+identifier).style.display="none";
    //        that.opened=false
    //    } else {
    //        document.getElementById("block"+identifier).style.display="block";
    //        that.opened=true;
    //    };
}

function videoSpoiler(identifier) {
        that = document.getElementById("spoiler"+identifier)
        if (that.opened) {
            document.getElementById("video"+identifier).style.display="none";
            that.opened=false
        } else {
            document.getElementById("video"+identifier).style.display="block";
            that.opened=true;
        };
}

$(document).ready(function(){
    $('.task').bind("cut copy paste",function(e) {
        e.preventDefault();
    });
});

//$(".spoiler-trigger").click(function() {
//    $(this).parent().next().collapse('toggle');
//});
