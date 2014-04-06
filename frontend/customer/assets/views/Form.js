// Filename: views/Form.js

define([
    'jquery',
    'underscore',
    'backbone',
    'models/Form',
    'models/FormResponse',
    'views/FormCard',
    'jquery.fullPage'
],
function($, _, Backbone, FormModel, FormResponseModel, FormCardView) {
    
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
            this.model.set( 'id', this.instanceID );

            // Save the form data
            this.model.save(this.responseModel.toJSON(), {
                'success': function(data) {
                    alert("Yeah!! The form got saved.");
                },
            });
        },

        render: function() {
            _.each(this.model.get('cards').models, this.addCard, this); // Append cards to the 'ol' of FormView
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
