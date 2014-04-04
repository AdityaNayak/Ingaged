// Filename: router.js

define([
    'jquery',
    'underscore',
    'backbone'
],
function($, _, Backbone){

    var Router = Backbone.Router.extend({
        routes: {
            'form/:instanceID': 'showForm',
            '*notFound': 'notFound'
        }
    });

    var initialize = function(){
        var appRouter = new Router;

        appRouter.on('route:showForm', function(){
            alert("The form will be shown here.");
        });

        appRouter.on('route:notFound', function(){
            alert("Nothing exists out here.");
        });

        Backbone.history.start();
    };

    return {
        'initialize': initialize
    }

});