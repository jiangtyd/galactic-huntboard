'use strict';

$( document ).ready(function() {
    $('#chatWrapper').resizable({
        alsoResize: '#chat, #callins',
        handles: 's',
        start: function() {
            $('#chatWrapper').addClass('noMouseEvents');
            $('#spreadsheetWrapper').addClass('noMouseEvents');
        },
        stop: function(e, ui) {
            $('#chatWrapper').removeClass('noMouseEvents');
            $('#spreadsheetWrapper').removeClass('noMouseEvents');
        }
    });
});