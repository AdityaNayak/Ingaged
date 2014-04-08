// Filename: app.js

define([
    'jquery',
    'underscore',
    'backbone',
    'Router'
],
function($, _, Backbone, Router) {
    
    var initialize = function(){
        // call our router's initialize function for a take off :D
        Router.initialize();
    }

    return {
        'initialize': initialize
    }

});
