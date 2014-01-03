var initApis = function() {
    gapi.load("auth:client,drive-realtime,drive-share", function() {} );
};

var initButtons = function() {
    var createFile = function() {
        $.post("/files/new", { name: $('#newpuzzlename').val() }, refreshFiles);
        $('#newpuzzlename').val('');
    };

    $('#newpuzzlebutton').on('click', createFile);
    $("#newpuzzlename").keyup(function (e) {
        if (e.keyCode == 13) {
            createFile();
        }
    });
};

var refreshFiles = function() {
    $.get("/files", function(data) {
        $('#filelistdiv').html(data.html);
    });
};

$(function() {
    //initApis();
    initButtons();
});
