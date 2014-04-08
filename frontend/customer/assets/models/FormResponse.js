// Filename: models/FormResponse.js

define([
    'underscore',
    'backbone'
],
function(_, Backbone){
    
    var FormResponseModel = Backbone.Model.extend({

        urlRoot: 'https://ingage-staging-1.herokuapp.com/customer/feedback',
        // urlRoot: 'http://localhost:5000/customer/feedback',

        defaults: {
            'field_responses': {},
            'nps_score': 7
        }

    });

    return FormResponseModel;

});
