// Filename: models/Form.js

define([
    'underscore',
    'backbone',
    'models/Merchant',
    'collections/FormCardCollection',
],

function(_, Backbone, MerchantModel, FormCardCollection){
    
    var FormModel = Backbone.Model.extend({
        urlRoot: 'http://localhost:5000/customer/feedback',
        parse: function(response){
            var cards;

            // Form data exists under the 'form' key of the response.
            response = response.form;

            // Add all the fields as cards. They will form the
            // first set of cards. NPS & Customer Details will
            // be added after that.
            cards = [];
            _.each(response.fields, function(field){
                cards.push(field);
            });
            delete response.fields;

            // TODO: Currently the ordering of cards is done in a very crude
            //       manner. This needs to be improved so that it can be dynamic.

            // Adding the NPS card
            cards.push({
                'type': 'NPS',
                'required': true,
                'text': response.nps_score_heading
            });
            delete response.nps_score_heading;

            // Adding the Feedback TextBox card
            cards.push({
                'type': 'FT',
                'required': false,
                'text': response.feedback_heading
            });
            delete response.feedback_heading;

            // Add the customer details card
            cards.push({
                'type': 'CD',
                'required': false,
                'text': response.customer_details_heading
            });
            delete response.customer_details_heading;

            // Add the 'cards' array to response as 'FormCardCollection'
            response.cards = new FormCardCollection(cards);

            // Add merchant details as 'MerchantModel'
            response.merchant = new MerchantModel(response.merchant);

            return response;
            
        },
    });

    return FormModel

});
