// Filename: router.js

define([
    'jquery',
    'underscore',
    'backbone',
    'views/Form'
],
function($, _, Backbone, FormView) {

    var Router = Backbone.Router.extend({
        routes: {
            ':instanceID': 'showForm', // Show the feedback form.
            '*notFound': 'notFound' // Anything other than showing of feedback form.
        }
    });

    var initialize = function() {
        var appRouter = new Router;

        appRouter.on('route:showForm', function(instanceID) {
            console.log("Feedback form with instance ID '" + instanceID + "' will be shown here.");
            new FormView( { 'instanceID' : instanceID } );
        });

        appRouter.on('route:notFound', function() {
            alert("Nothing exists out here.");
        });

        Backbone.history.start();
    };

    return {
        'initialize': initialize
    }

});
