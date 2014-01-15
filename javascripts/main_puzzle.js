'use strict';

$( document ).ready(function() {
    $('#spreadsheetWrapper').height($(window).height()-$("#chatWrapper").height());

    window.onresize = function(event) {
        $('#spreadsheetWrapper').height($(window).height()-$("#chatWrapper").height());
    }

    $('#chatWrapper').resizable({
        alsoResize: '#chat',
        alsoResizeReverse: '#spreadsheetWrapper',
        handles: 's',
        minHeight: 25,
        resize: function() {
            $('#spreadsheetWrapper').height($(window).height()-$("#chatWrapper").height()-$("callins").height());
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