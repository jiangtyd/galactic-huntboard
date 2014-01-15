'use strict';

$( document ).ready(function() {
    $('#puzzlesheet').height($(window).height()-$("#callins").height());
    window.onresize = function(event) {
        $('#puzzlesheet').height($(window).height()-$("#callins").height());
    }
});