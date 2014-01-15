'use strict';

$( document ).ready(function() {
    $('#chatWrapper').resizable({
        alsoResize: '#chat',
        handles: 's',
        minHeight: 115,
        start: function() {
            $('#chatWrapper').addClass('noMouseEvents');
            $('#spreadsheetWrapper').addClass('noMouseEvents');
        },
        stop: function(e, ui) {
            $('#chatWrapper').removeClass('noMouseEvents');
            $('#spreadsheetWrapper').removeClass('noMouseEvents');
        }
    });


    document.getElementById("chatWrapper").onmouseenter = disable_scroll;
    document.getElementById("chatWrapper").onmouseleave = enable_scroll;

});

function disable_scroll()
{
    document.getElementById("bodyId").style.overflow="hidden";
}

function enable_scroll()
{
    document.getElementById("bodyId").style.overflow="auto";
}