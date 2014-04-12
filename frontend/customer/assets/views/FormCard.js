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
    'text!templates/cards/input.html',
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

        cardCSSClasses: {
            'CU_HTML': 'display-card',
            'YN': 'yes-no',
            'ST': 'multiple rating',
            'MT': 'multiple',
            'TT': 'small-input',
            'FT': 'large-input',
            'NPS': 'input-slider',
            'CD': 'customer-details'
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
            'click .done': 'moveCardDown',

            // Clicking on the display card should mvoe the card down
            'click .display-container': 'moveCardDown',

            // Clicking on the "Submit" button will do the Customer Details card
            // validation & then trigger an event which will be caught by views/Form.js
            'click #form-submit-btn': 'submitFeedback'


        },

        initialize: function(options) {
            var template;

            this.model = options.model;
            this.responseModel = options.responseModel;
            // Template is there in the 'text' attribute of model if it is a display card
            if ( this.model.get('type') == 'CU_HTML' ) template = _.template( this.model.get('text') );
            else template = _.template( this.cardTemplates[this.model.get('type')], this.model.toJSON() );
            this.template = template;
            this.filled = false;
        },

        submitFeedback: function(e) {
            // Activate the required flag in Customer Details card model
            // if NPS score is below 7 else deactivate it.
            if ( this.responseModel.get('nps_score') <= 7 ) this.model.set( 'required', true );
            else this.model.set( 'required', false );
            
            // Do the card validation & return if it is not validated
            if ( this.validateCard() ) {
                $(e.currentTarget).trigger('submitFeedback');
            }
        },

        showDone: function() {
            this.$el.find('.done.hide').show();
        },

        validateCard: function() {
            $('.section.active').removeClass('rq rq-rm');
            if ( this.model.get('required') && !this.filled ) {
                $('.section.active').addClass('rq').delay(200).queue(function(next){
                    $(this).addClass("rq-rm");
                    next();
                });
                return false; // false in case the filled flag of the view is not active
            };
            return true // true in case the filled flag of the view is not active
        },

        moveCardDown: function() {
            if ( !this.validateCard() ) return
            $.fn.fullpage.actualMoveSectionDown();
        },

        moveCardUp: function() {
            $.fn.fullpage.actualMoveSectionUp();
        },

        textCardKeyUp: function(e) {
            var currentTarget, rM;

            e.preventDefault();

            currentTarget = $(e.currentTarget);

            // TextBox Card
            if ( this.model.get('type') == 'TT' ) {
                // Mark card as not filled if the val() returns an empty string
                if ( currentTarget.val() == "" ){
                    this.filled = false;
                    return;
                }
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
                rM = this.responseModel;
                // Mark card as filled only if all of the three customer details are filled.
                if ( rM.get('customer_name') && rM.get('customer_mobile') && rM.get('customer_email') ) this.filled = true;
                // Switch the filled flag off if the contents of a field are deleted by the user
                if ( currentTarget.val() == "" ) {
                    this.filled = false;
                    this.responseModel.set( currentTarget.attr('name'), null );
                }
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
            // Add card specific CSS class
            this.$el.addClass(this.cardCSSClasses[this.model.get('type')]);
            this.$el.html(this.template);
            if ( this.model.get('type') == 'NPS' ) this.addNoUiSlider();
            return this
        },

    });

    return FormCardView;

});
