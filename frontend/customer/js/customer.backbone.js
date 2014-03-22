$( document ).ready(function() {
	/* serializs a form into a JS object */
	$.fn.serializeObject = function() {
		var o = {};
		var a = this.serializeArray();
		$.each(a, function() {
			if (o[this.name] !== undefined) {
				if (!o[this.name].push) {
					o[this.name] = [o[this.name]];
				}
				o[this.name].push(this.value || '');
			} else {
				o[this.name] = this.value || '';
			}
		});
		return o;
	};

	/* all the routes */
	var Router = Backbone.Router.extend({
		routes: {
			":instance_id": "feedbackForm",
		}
	});

	/* hostname of the api */
	var api_root = 'https://ingage-staging-3.herokuapp.com'

	/* feedback form model */
	FeedbackFormModel = Backbone.Model.extend({
		urlRoot: api_root + "/customer/feedback",
		parse: function(response, xhr){
            if (response.form){
                return response.form;
            } else {
                return response;
            }
		},
	});

	/* feedback form view */
	var FeedbackFormView = Backbone.View.extend({
		
		el: 'body',
        successTemplate: _.template($("#feedback-form-success-template").html()),
		events: {
			'click input,textarea': 'showDone',
			'click .intr-btn, .intr': 'nextSection',
			'click #form-submit-btn': 'submitFeedback',
		},
		nextSection: function(ev){

			var previousResponse = $(ev.currentTarget).parent().find(".response");
			if (previousResponse) {
			    previousResponse.removeClass("response");
			}
			$(ev.currentTarget).addClass("response");
			$.fn.fullpage.moveSectionDown();
		},
		showDone: function(ev){
			var donebutton = $('.done');
			$(donebutton).fadeIn(300);
			ev.stopPropagation();
		},
		submitFeedback: function(ev){
			ev.preventDefault();

            /* responses to indivual fields */
            var field_responses = {} // dict storing the field responses
            var sections = $(".multiple.rating, .multiple, .small-input, .yes-no");
            $.each(sections, function(i){
                section = $(sections[i]);
                field_id = section.find('input[name="field_id"]').val();
                if (!section.hasClass("small-input")){
                    response = section.find('.response').attr('response');
                }
                else {
                    response = section.find('input[name="tt_response"]').val();
                }
                field_responses[field_id] = response || ".";
            });

            /* feedback text */
            var feedback_text = $(".large-input").find("textarea").val() || ".";

            // nps score
            var nps_score = $(".input-slider").find("#show-serialization-field-nps").text();

            // price value score
            var price_value_score = $(".input-slider").find("#show-serialization-field-price-value").text();

			
            /* customer details */
            var customer_details = {
                'name': $(".customer-details").find("input[name='name']").val(),
                'email': $(".customer-details").find("input[name='email']").val(),
                'mobile': $(".customer-details").find("input[name='phone']").val()
            };

            /* complete data to send to the server */
            var data = {
                'feedback_text': feedback_text,
                'nps_score': nps_score,
                'field_responses': field_responses,
                'id': $("input[name='id']").val()
            }
            if (price_value_score){
                data.price_value_score = price_value_score;
            }
			if (!customer_details.name == ""){
				data.customer_name = customer_details.name
			}
			if (!customer_details.email == ""){
				data.customer_email = customer_details.email
			}
			if (!customer_details.mobile == ""){
				data.customer_mobile = customer_details.mobile
			}

			var that = this;
			var feedbackForm = new FeedbackFormModel();
			feedbackForm.save(data, {
			    'success': function(feedback){
                    that.$el.html(that.successTemplate({'feedback': feedback, 'instance_id': that.instanceID}));
			        // reload the page after 5 seconds
			        //setTimeout(function(){
			        //    location.reload();
			        //}, 5 * 1000);
			    }
			});
		},
		render: function(options){
			var feedbackForm = new FeedbackFormModel({'id': options.instance_id})
			var that = this;
			feedbackForm.fetch({
				'success': function(form){
					that.form = form;
					that.instanceID = options.instance_id
					var template = _.template($("#feedback-form-template").html(), {instance_id: options.instance_id, form: form});
					that.$el.html(template);
					
					
				    $.fn.fullpage({
				        verticalCentered: false,
				        resize : false,
				        scrollingSpeed: 150,
				        easing: false,
				        menu: false,
				        navigation: false,
				        slidesNavigation: false,
				        loopBottom: false,
				        loopTop: false,
				        loopHorizontal: false,
				        autoScrolling: true,
				        scrollOverflow: false,
				        css3: true,
				        paddingTop: '10px',
				        paddingBottom: '10px',
				        keyboardScrolling: false,
				        touchSensitivity: 5,

				        //events
				        onLeave: function(index, direction){},
				        afterLoad: function(anchorLink, index){},
				        afterRender: function(){
				        	$("#nps-rating").noUiSlider({
								range: [0, 10],
								start: 7,
								step: 1,
								handles: 1,
								serialization: {
									resolution: 1,
									to: [$("#show-serialization-field-nps"), "html"]
								},
							});
				        	$("#price-value-rating").noUiSlider({
								range: [0, 10],
								start: 7,
								step: 1,
								handles: 1,
								serialization: {
									resolution: 1,
									to: [$("#show-serialization-field-price-value"), "html"]
								},
							});
				        },
				        afterSlideLoad: function(anchorLink, index, slideAnchor, slideIndex){},
				        onSlideLeave: function(anchorLink, index, slideIndex, direction){
				        	if(temp===1){
				        	}
				        }
				    });
					


					return
					
				},
				'error': function(collection,response){
					var template = _.template($("#feedback-form-not-exists-template").html(), {})
					that.$el.html(template);
					return
				},
			})
		}
	});
var feedbackFormView = new FeedbackFormView();    

var router = new Router();

/* feedback form view */
router.on('route:feedbackForm', function(instance_id){
	feedbackFormView.render({instance_id: instance_id});
})

Backbone.history.start();
});
