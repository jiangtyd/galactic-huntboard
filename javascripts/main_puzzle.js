'use strict';

$( document ).ready(function() {
    var CHAT_STATUS_BAR_HEIGHT = 20;
    $('#spreadsheetWrapper').height($(window).height()-$("#chatWrapper").height()-CHAT_STATUS_BAR_HEIGHT);

    window.onresize = function(event) {
        $('#spreadsheetWrapper').height($(window).height()-$("#chatWrapper").height()-CHAT_STATUS_BAR_HEIGHT);
    }

    $('#chatWrapper').resizable({
        alsoResize: '#chat',
        alsoResizeReverse: '#spreadsheetWrapper',
        handles: 's',
        minHeight: 80,
        resize: function() {
            $('#spreadsheetWrapper').height($(window).height()-$("#chatWrapper").height()-$("callins").height()-CHAT_STATUS_BAR_HEIGHT);
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