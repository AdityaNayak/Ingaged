// Filename: FormCardCollection.js

define([
    'underscore',
    'backbone',
    'models/FormCard'
],
function(_, Backbone, FormCardModel){
    
    var FormCardCollection = Backbone.Collection.extend({
        model: FormCardModel
    });

    return FormCardCollection;

});
