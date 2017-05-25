onload = function(){
    face_rect();
};

function face_rect() {
    var canvas = document.getElementById('image_canvas');
    if ( ! canvas || ! canvas.getContext ) {
        return false;
    }
    facex = facex.substr(1,facex.length-2).split(",");
    facey = facey.substr(1,facey.length-2).split(",");
    facew = facew.substr(1,facew.length-2).split(",");
    faceh = faceh.substr(1,faceh.length-2).split(",");
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
        for(var i = 0; i < facex.length; i++){
            var rectx = Number(facex[i]);
            var recty = Number(facey[i]);
            var rectw = Number(facew[i]);
            var recth = Number(faceh[i]);
            ctx.strokeRect(rectx,recty,rectw,recth);
        }
    }
}

function draw_image(){
    
}