// Filename: views/FormCard

define([
    'jquery',
    'underscore',
    'backbone',
    // Templates of all supported cards.
    'text!templates/cards/customer_details.html',
    'text!templates/cards/feedback_text.html',
    'text!templates/cards/multiple_choice.html',
    'text!templates/cards/nps.html',
    'text!templates/cards/star_rating.html',
    'text!templates/cards/textbox.html',
    'text!templates/cards/yes_no.html',
    // jquery fullPage
    'jquery.fullPage',
    // noUiSlider
    'jquery.nouislider'
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

        events: {

            // Updating the element showing the NPS Score
            'change #nps-rating': 'updateNpsScore',
            'set #nps-rating': 'updateNpsScore',
            'slide #nps-rating': 'updateNpsScore',

            'click .intr-btn, .intr': 'onChoiceClick'
        },

        initialize: function(options) {
            this.className = 'row'
            this.model = options.model;
            this.template = _.template( this.cardTemplates[this.model.get('type')], this.model.toJSON() );
        },

        onChoiceClick: function() {
            $.fn.fullpage.moveSectionDown();
        },

        updateNpsScore: function(event, number) {
            number = Number(number);
            this.$el.find("#show-serialization-field").html(number);
        },

        addNoUiSlider: function() { // Adds noUiSlider to '#nps-rating' element
            var npsStart;

            npsStart = 7;
            this.$el.find('#nps-rating').noUiSlider({
                start: npsStart,
                step: 1,
                range: {
                    'min': 1,
                    'max': 10
                },
            });
            this.$el.find("#show-serialization-field").html(npsStart);
        },

        render: function() {
            this.$el.html(this.template);
            if ( this.model.get('type') == 'NPS' ) this.addNoUiSlider();
            return this
        },

    });

    return FormCardView;

});
