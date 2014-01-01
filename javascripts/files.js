$(function() {
    $('#newpuzzlebutton').on('click', function() {
        $.post("/makefile", { name: $('#newpuzzlename').val() });
        $('#newpuzzlename').val('');
    });
});
