// Filename: models/FormResponse.js

define([
    'underscore',
    'backbone'
],
function(_, Backbone){
    
    var FormResponseModel = Backbone.Model.extend({

        urlRoot: 'https://ingage.herokuapp.com/customer/feedback',

        defaults: {
            'field_responses': {},
            'nps_score': 7
        }

    });

    return FormResponseModel;

});
