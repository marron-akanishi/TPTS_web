$(function(){
    $("#idtext").keydown(function(e) {
        if ((e.which && e.which === 13) || (e.keyCode && e.keyCode === 13)) {
            $('#jump').click();
        }
    });

    $('html').keyup(function(e){
        switch(e.which){
            case 37: // Key[←]
                $("#prev").click();
                break;
 
            case 39: // Key[→]
                $("#next").click();
                break;
        }
    });
});