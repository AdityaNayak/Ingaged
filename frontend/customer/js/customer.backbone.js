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
    var api_root = 'https://ingage.herokuapp.com'

    /* feedback form model */
    var FeedbackFormModel = Backbone.Model.extend({
        urlRoot: api_root + "/customer/feedback",
        parse: function(response, xhr){
            return response.form;
        },
    });

    /* feedback form view */
    var FeedbackFormView = Backbone.View.extend({
        el: 'body',
        successTemplate: _.template($("#feedback-form-success-template").html(), {}),
        events: {
            'click a': 'nextSection',
            'submit #comment-form': 'submitFeedback',
        },
        nextSection: function(ev){
            if (!$("#comment")[0].checkValidity()){
                $(".error").show();
                setTimeout(function(){
                   $(".error").hide();
                   $(".error").fadeOut(500);
                   },5000);
                return
            }
            $(".error").hide();
            $(".commentsection").hide();
            $(".contactdetails").show();
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
