// Filename: models/FormResponse.js

define([
    'underscore',
    'backbone'
],
function(_, Backbone){
    
    var FormResponseModel = Backbone.Model.extend({
        urlRoot: 'http://192.168.1.106:5000/customer/feedback',
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
