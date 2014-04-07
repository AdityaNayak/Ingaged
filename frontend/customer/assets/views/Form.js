// Filename: views/Form.js

define([
    'jquery',
    'underscore',
    'backbone',
    'models/Form',
    'models/FormResponse',
    'views/FormCard',
    'text!templates/success_thanks.html',
    'jquery.fullPage'
],
function($, _, Backbone, FormModel, FormResponseModel, FormCardView, SuccessThanksTemplate) {
    
    var FormView = Backbone.View.extend({

        tagName: 'ol',

        className: 'section-list',

        events: {
            'click #form-submit-btn': 'submitFeedback'
        },

        initialize: function(options) {
            this.instanceID = options.instanceID;
            this.model = new FormModel( { 'id': options.instanceID } );
            this.model.on('sync', this.render, this);
            
            this.responseModel = new FormResponseModel();

            this.model.fetch();
        },

        submitFeedback: function() {
            // set the ID to the ID of the instance.
            // This gets changed to the ID of the form when the del is fetched.
            this.responseModel.set( 'id', this.instanceID );

            // Save the form data
            var that = this;
            this.responseModel.save( this.responseModel.toJSON(), {
                'success': function(data) {
                    var successTemplate = _.template(SuccessThanksTemplate);
                    $('body').html(successTemplate);
                },
            });
        },

        render: function() {
            _.each(this.model.get('cards').models, this.addCard, this); // Append cards to the 'ol' of FormView
            this.$el.addClass(this.model.get('css_class_name'));
            $('body').html(this.$el);
            this.activateFullPage();
        },

        addCard: function(cardModel) {
            var cardView;
            cardView = new FormCardView( { 'model': cardModel, 'responseModel': this.responseModel } );
            this.$el.append( cardView.render().$el );
        },

        activateFullPage: function() {
            $.fn.fullpage({
                easing: false,
                css3: true,
                verticalCentered: false,
                touchSensitivity: 2
            });
        }

    });

    return FormView;

});