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
	var api_root = 'localhost:5000'

	/* feedback form model */
	FeedbackFormModel = Backbone.Model.extend({
		urlRoot: "http://" + api_root + "/customer/feedback",
		parse: function(response, xhr){
			return response.form;
		},
	});

	/* feedback form view */
	var FeedbackFormView = Backbone.View.extend({
		
		el: 'body',

		successTemplate: _.template($("#feedback-form-success-template").html(), {}),
		events: {
			'click input,textarea': 'showDone',
			'click .intr-btn, .intr': 'nextSection',
			'click .form-submit-btn': 'submitFeedback',
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
                field_responses[field_id] = response;
            });

            /* feedback text */
            var feedback_text = $(".large-input").find("textarea").val();

            /* nps score */
            var nps_score = $(".input-slider").find(".nps-score").text();
			
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
			if (!customer_details.name == ""){
				data.customer_name = customer_details.name
			}
			if (!customer_details.email == ""){
				data.customer_email = customer_details.email
			}
			if (!customer_details.mobile == ""){
				data.customer_mobile = customer_details.mobile
			}

			var feedbackForm = new FeedbackFormModel();
			feedbackForm.save(data);
			this.$el.html(this.successTemplate);
		},
		render: function(options){
			var feedbackForm = new FeedbackFormModel({'id': options.instance_id})
			var that = this;
			feedbackForm.fetch({
				'success': function(form){
					var template = _.template($("#feedback-form-template").html(), {instance_id: options.instance_id, form: form});
					that.$el.html(template);
					$("#nps-rating").noUiSlider({
							range: [0, 10],
							start: 7,
							step: 1,
							handles: 1,
							serialization: {
								resolution: 1,
								to: [ $("#show-serialization-field"),"html" ]
							}
						});
					
					$.fn.fullpage({
				        verticalCentered: false,
				        resize : false,
				        scrollingSpeed: 450,
				        easing: false,
				        anchors: [],
				        menu: false,
				        navigation: false,
				        slidesNavigation: false,
				        loopBottom: false,
				        loopTop: true,
				        loopHorizontal: false,
				        autoScrolling: true,
				        scrollOverflow: false,
				        css3: true,
				        paddingTop: '3em',
				        paddingBottom: '10px',

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
