define([
    'jquery',
    'underscore',
    'backbone',
    'router'
],
function($, _, Backbone, Router){
    
    var initialize = function(){
        // call our router's initialize function to take off :D
        Router.initialize();
    }

    return {
        'initialize': initialize
    }

});
