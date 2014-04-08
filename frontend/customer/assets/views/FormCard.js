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
    'text!templates/cards/custom_html.html',
    // jquery fullPage
    'jquery.fullPage',
    // noUiSlider
    'jquery.nouislider'
],
function($, _, Backbone, CDCardTemplate, FTCardTemplate, MTCardTemplate, NPSCardTemplate, STCardTemplate,
    TTCardTemplate, YNCardTemplate, CuHTMLCardTemplate) {
    
    var FormCardView = Backbone.View.extend({
        
        cardTemplates: {
            'CU_HTML': CuHTMLCardTemplate,
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

            // User clicks a choice on Yes/No, Multiple Choice or Star Rating card.
            'click .intr-choice': 'onChoiceClick',

            // Recording changes on TextBox Card, Feedback TextArea & Customer Details Card
            'keyup input[name=tt_response]': 'textCardKeyUp', // TextBox card
            'keyup .feedback-text': 'textCardKeyUp', // Feedback TextArea
            'keyup input[name^="customer"]': 'textCardKeyUp', // Customer Details card

            // Scrolling cards Up & Down
            'moveSectionDown': 'moveCardDown',
            'moveSectionUp': 'moveCardUp',

            // Showing done button on TextBox Card & Feedback TextArea
            'click input[name=tt_response]': 'showDone',
            'click .feedback-text': 'showDone',

            // Clicking on done will move the card down
            'click .done': 'moveCardDown'

        },

        initialize: function(options) {
            this.model = options.model;
            this.responseModel = options.responseModel;
            this.template = _.template( this.cardTemplates[this.model.get('type')], this.model.toJSON() );
            this.filled = false;
        },

        showDone: function() {
            this.$el.find('.done.hide').show();
        },

        moveCardDown: function() {
            if ( this.model.get('required') && !this.filled ) {
                    $('.section.active').addClass('rq').delay(200).queue(function(next){
                    $(this).addClass("rq-rm");
                    next();
                });

                return;
            };
            $.fn.fullpage.actualMoveSectionDown();
        },

        moveCardUp: function() {
            $.fn.fullpage.actualMoveSectionUp();
        },

        textCardKeyUp: function(e) {
            var currentTarget;

            e.preventDefault();

            currentTarget = $(e.currentTarget);

            // TextBox Card
            if ( this.model.get('type') == 'TT' ) {
                this.filled = true;
                this.responseModel.attributes.field_responses[this.model.get('id')] = currentTarget.val();
                return;
            }

            // Feedback Text Card
            if ( this.model.get('type') == 'FT' ) {
                this.filled = true;
                this.responseModel.set ('feedback_text', currentTarget.val() );
                return;
            }

            // Customer Details Card
            if (this.model.get('type') == 'CD' ) {
                this.filled = true;
                this.responseModel.set( currentTarget.attr('name'), currentTarget.val() );
                return
            }
        },

        onChoiceClick: function(e) {
            var response, currentTarget;

            e.preventDefault();

            currentTarget = $(e.currentTarget); 
            response = currentTarget.data('response');

            // Add the response to the responseModel
            if ( ['YN', 'ST', 'MT'].indexOf(this.model.get('type')) != -1 ) {
                this.filled = true;
                this.responseModel.attributes.field_responses[this.model.get('id')] = response;
            }

            // Add a class to response choice & remove it from any others if it exists
            this.$el.find('.response.intr-choice').removeClass('response');
            currentTarget.addClass('response');

            $.fn.fullpage.moveSectionDown();
        },

        updateNpsScore: function(e, number) {
            number = Number(number);
            this.$el.find("#show-serialization-field").html(number);

            // Update the response model.
            this.filled = true;
            this.responseModel.set( 'nps_score', number );
        },

        addNoUiSlider: function() {
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
