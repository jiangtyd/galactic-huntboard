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
});