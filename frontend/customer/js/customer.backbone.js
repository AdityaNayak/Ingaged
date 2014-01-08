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
	var api_root = 'ingage.herokuapp.com'

	/* feedback form model */
	var FeedbackFormModel = Backbone.Model.extend({
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
			'submit #comment-form': 'submitFeedback',
		},
		nextSection: function(ev){
			$.fn.fullpage.moveSectionDown();
		},
		showDone: function(ev){
			var donebutton = $('.done');
			$(donebutton).fadeIn(300);
			ev.stopPropagation();
		},
		submitFeedback: function(ev){
			ev.preventDefault();
			serializedForm = $(ev.currentTarget).serializeObject();
			data = {"text": serializedForm.comment, "id": serializedForm.id}
			if (!serializedForm.name == ""){
				data.customer_name = serializedForm.name
			}
			if (!serializedForm.email == ""){
				data.customer_email = serializedForm.email
			}
			if (!serializedForm.phone == ""){
				data.customer_mobile = serializedForm.phone
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
