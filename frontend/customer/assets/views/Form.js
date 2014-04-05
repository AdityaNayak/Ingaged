// Filename: views/Form.js

define([
    'jquery',
    'underscore',
    'backbone',
    'models/Form',
    'views/FormCard',
    'jquery.fullPage'
],
function($, _, Backbone, FormModel, FormCardView) {
    
    var FormView = Backbone.View.extend({

        tagName: 'ol',

        className: 'section-list',

        initialize: function(options) {
            this.model = new FormModel( { 'id': options.instanceID } );
            this.model.on('sync', this.render, this);
            this.model.fetch();
        },

        render: function() {
            _.each(this.model.get('cards').models, this.addCard, this); // Append cards to the 'ol' of FormView
            $('body').html(this.$el);
            this.activateFullPage();
        },

        addCard: function(cardModel) {
            var cardView;
            cardView = new FormCardView( { 'model': cardModel } );
            this.$el.append( cardView.render().$el );
        },

        activateFullPage: function() {
            $.fn.fullpage({
                easing: false,
                css3: true,
                touchSensitivity: 2
            });
        }

    });

    return FormView;

});
