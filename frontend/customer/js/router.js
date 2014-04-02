define([
    'jquery',
    'underscore',
    'backbone'
],
function($, _, Backbone){

    var Router = Backbone.Router.extend({
        routes: {
            'form/:instanceID': 'showForm',
            '*actions': 'defaultAction'
        }
    });

    console.log("dasda");
    var initialize = function(){
        var appRouter = new Router;

        appRouter.on('route:showForm', function(){
            alert("The form will be shown here.");
        });

        appRouter.on('route:defaultAction', function(actions){
            alert("Nothing exists out here.");
        });

        Backbone.history.start();
    };

    return {
        'initialize': initialize
    }

});
