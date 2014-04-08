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
            'submitFeedback #form-submit-btn': 'submitFeedback'
        },

        initialize: function(options) {
            this.instanceID = options.instanceID;
            this.model = new FormModel( { 'id': options.instanceID } );
            this.model.on('sync', this.render, this);
            
            this.responseModel = new FormResponseModel();

            this.model.fetch();
        },

        submitFeedback: function() {
            $('#form-submit-btn').fadeOut(300);
            $('#btn-loading').delay(300).fadeIn(300);

            // set the ID to the ID of the instance.
            // This gets changed to the ID of the form when the del is fetched.
            this.responseModel.set( 'id', this.instanceID );

            // Save the form data
            var that = this;
            this.responseModel.save( this.responseModel.toJSON(), {
                'success': function(data) {
                    var successTemplate = _.template( SuccessThanksTemplate, that.responseModel.toJSON() );
                    $('body').html(successTemplate);
                    // Page will reload 10 seconds after feedback has been submitted
                    setTimeout(function() {
                        location.reload(); 
                    }, 10 * 1000);
                },
                'error': function(data) {
                    $('#btn-loading').fadeOut(300);
                    $('#form-submit-btn').delay(300).fadeIn(300);
                }
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
