// Filename: views/FormCard

define([
    'jquery',
    'underscore',
    'backbone',
    // Templates of all supported cards.
    'text!templates/cards/customer_details.html',
    'text!templates/cards/feedback_text.html',
    'text!templates/cards/multiple_choice.html',
    'text!templates/cards/nps_card.html',
    'text!templates/cards/star_rating.html',
    'text!templates/cards/textbox.html',
    'text!templates/cards/yes_no.html'
],
function($, _, Backbone, CDCardTemplate, FTCardTemplate, MTCardTemplate, NPSCardTemplate, STCardTemplate,
    TTCardTemplate, YNCardTemplate) {
    
    var FormCardView = Backbone.View.extend({
        
        cardTemplates: {
            'CD': CDCardTemplate,
            'FT': FTCardTemplate,
            'MT': MTCardTemplate,
            'NPS': NPSCardTemplate,
            'ST': STCardTemplate,
            'TT': TTCardTemplate,
            'YN': YNCardTemplate
        },

        tagName: 'div',

        className: 'section row',

        initialize: function(options) {
            this.className = 'row'
            this.model = options.model;
            this.template = _.template( this.cardTemplates[this.model.get('type')], this.model.toJSON() );
        },

        render: function() {
            this.$el.html(this.template);
            return this
        }

    });

    return FormCardView;

});
