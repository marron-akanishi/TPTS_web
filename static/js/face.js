onload = function(){
    face_rect();
};

$('#detailtab a').click(function (e) {
  e.preventDefault()
  $(this).tab('show')
})

function face_rect() {
    var canvas = document.getElementById('image_canvas');
    if ( ! canvas || ! canvas.getContext ) {
        return false;
    }
    var ctx = canvas.getContext('2d');
    var img = new Image();
    img.src = image_url;
    img.onload = function() {
        canvas.setAttribute("width", img.width.toString());
        canvas.setAttribute("height", img.height.toString());
        ctx.drawImage(img, 0, 0);
        ctx.beginPath();
        ctx.strokeStyle = 'rgb(00,255,00)';
        ctx.lineWidth = 3;
        for(var i = 0; i < eval(facex).length; i++){
            var rectx = Number(eval(facex)[i]);
            var recty = Number(eval(facey)[i]);
            var rectw = Number(eval(facew)[i]);
            var recth = Number(eval(faceh)[i]);
            ctx.strokeRect(rectx,recty,rectw,recth);
        }
    }
}

function draw_image(){
    
}