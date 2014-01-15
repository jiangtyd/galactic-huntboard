'use strict';

$( document ).ready(function() {
    $('#spreadsheetWrapper').height($(window).height()-$("#chatWrapper").height()+90);

    window.onresize = function(event) {
        $('#spreadsheetWrapper').height($(window).height()-$("#chatWrapper").height()+90);
    }

    $('#chatWrapper').resizable({
        alsoResize: '#chat',
        alsoResizeReverse: '#spreadsheetWrapper',
        handles: 's',
        minHeight: 115,
        resize: function() {
            $('#spreadsheetWrapper').height($(window).height()-$("#chatWrapper").height()+90);
        },
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