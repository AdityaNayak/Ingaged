// Filename: models/Form.js

define([
    'underscore',
    'backbone',
    'models/Merchant',
    'collections/FormCardCollection',
],

function(_, Backbone, MerchantModel, FormCardCollection) {
    
    var FormModel = Backbone.Model.extend({
        urlRoot: 'https://ingage.herokuapp.com/customer/feedback',
        parse: function(response){
            var cards, noFields;

            // Response should be returned as such when the form data is being saved.
            // This would occur in the case of a PUT request.
            if ( response.hasOwnProperty('success') ) {
                return response;
            }

            // Form data exists under the 'form' key of the response.
            response = response.form;

            // Activate the no fields flag if required
            noFields = false;
            if ( response.fields.length == 0 ) noFields = true;

            // Cards array
            cards = [];

            // Add the custom HTML card as the first one
            cards.push({
                'type': 'CU_HTML',
                'required': false,
                'text': response.display_card_html
            });

            // Add all the fields as cards. They will form the
            // first set of cards. NPS & Customer Details will
            // be added after that.
            _.each(response.fields, function(field){
                cards.push(field);
            });
            delete response.fields;

            // TODO: Currently the ordering of cards is done in a very crude
            //       manner. This needs to be improved so that it can be dynamic.

            // Push the Feedback TextBox card first if there are no fields
            if (noFields) {
                cards.push({
                    'type': 'FT',
                    'required': false,
                    'text': response.feedback_heading
                });
                delete response.feedback_heading;
            }

            // Adding the NPS card
            cards.push({
                'type': 'NPS',
                'required': false,
                'text': response.nps_score_heading
            });
            delete response.nps_score_heading;

            // Adding the Feedback TextBox card
            if (!noFields) {
                cards.push({
                    'type': 'FT',
                    'required': false,
                    'text': response.feedback_heading
                });
                delete response.feedback_heading;
            }

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
