jQuery(function($){
    $("form").submit(function(event){
        dispLoading("画像取得中...");
        event.preventDefault();
        var $form = $(this);
        $.ajax({
            url: '/makelist',
            type: 'POST',
            data: $form.serialize(),
            beforeSend: function(xhr, settings) {
                // ボタンを無効化し、二重送信を防止
                $(".btn").attr('disabled', true);
            },
            success:function(resultdata) {
                location.href=resultdata
            },
            error: function(error) {
                alert('取得に失敗しました');
            },
            complete : function(data) {
                // Loadingイメージを消す
                $(".btn").attr('disabled', false);
                removeLoading();
            }
        });
    });
});

// Loadingイメージ表示関数
function dispLoading(msg){
    // 画面表示メッセージ
    var dispMsg = "";
 
    // 引数が空の場合は画像のみ
    if( msg != "" ){
        dispMsg = "<div class='loadingMsg'>" + msg + "</div>";
    }
    // ローディング画像が表示されていない場合のみ表示
    if($("#loading").size() == 0){
        $("body").append("<div id='loading'>" + dispMsg + "</div>");
    } 
}
 
// Loadingイメージ削除関数
function removeLoading(){
 $("#loading").remove();
}