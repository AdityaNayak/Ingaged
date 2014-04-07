// Filename: models/FormResponse.js

define([
    'underscore',
    'backbone'
],
function(_, Backbone){
    
    var FormResponseModel = Backbone.Model.extend({
        urlRoot: 'https://ingage-staging-1.herokuapp.com/customer/feedback',
        defaults: {
            'feedback_text': null,
            'nps_score': 7,
            'customer_name': null,
            'customer_phone': null,
            'customer_email': null,
            'field_responses': {}
        }
    });

    return FormResponseModel;

});
