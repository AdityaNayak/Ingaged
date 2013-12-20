$( document ).ready(function() {

    /* serializes a form into a JS object */
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

    /* all the routes of the merchant dashboard */
    var Router = Backbone.Router.extend({
        routes: {
            "": "login",
            "timeline": "feedbackTimeline",
            "feedback_forms": "feedbackForms",
            "feedback_forms/new": "newFeedbackForm",
            "feedback_forms/:form_id/instances": "formInstancesList",
            "feedback_forms/:form_id/instances/new": "newFormInstances"
        }
    });
        
    /* hostname of the api server */
    var api_root = 'ingage.herokuapp.com'


    var UserCredentialsModel = Backbone.Model.extend();
    var userCredentialsModel = new UserCredentialsModel();

    /* collection storing the list of feedbacks which come in the timeline */
    var FeedbackTimelineCollection = Backbone.Collection.extend({
        url: "http://" + api_root + "/dashboard/timeline",
        parse: function(response, xhr){
            return response.feedbacks;
        }
    });

    /* collection of the list of feedback forms of the merchant */
    var FeedbackFormsCollection = Backbone.Collection.extend({
        url: "http://" + api_root + "/dashboard/forms",
        parse: function(response, xhr){
            return response.forms;
        }
    });

    /* collection of instances of a form */
    var FormInstancesCollection = Backbone.Collection.extend({
        initialize: function(options){
            this.id = options.id;
        },
        url: function(){
            return "http://" + api_root + "/dashboard/forms/" + this.id + "/instances"
        },
        parse: function(response, xhr){
            return response.instances 
        }
    });
    
    /* model of the feedback form */
    var FormModel = Backbone.Model.extend({
        urlRoot: "http://" + api_root + "/dashboard/forms",
        parse: function(response, xhr){
            return response.form
        }
    });

    /* model of the instance attached to the feedback form */
    var InstanceModel = Backbone.Model.extend({
        initialize: function(props){
            this.form_id = props.form_id;
        },
        urlRoot: function(){
            return "http://" + api_root + "/dashboard/forms/" + this.form_id + "/instances"
        }
    });

    /* login page */
    var LoginView = Backbone.View.extend({
        el: '.main-app',
        events: {
            'submit #login-form': 'loginUser'
        },
        loginUser: function(ev){
            ev.preventDefault();
            var credentials = $(ev.currentTarget).serializeObject();
            $.ajax({
                type: "GET",
                url: "http://" + api_root + "/dashboard/auth/check_credentials",
                headers: Backbone.BasicAuth.getHeader({ username: credentials.username, password: credentials.password }),
                success: function(data){
                    userCredentialsModel.username = credentials.username;
                    userCredentialsModel.password = credentials.password;
                    router.navigate('timeline', {trigger: true});
                },
                    error: function(data){
                    $(".error").show();
                    $("#login-form").removeClass("login-form");
                        setTimeout(function(){
                           $(".error").hide();
                           $("#login-form").addClass("login-form");
                           },5000);
                } 
            });
        },
        render: function(){
            if (userCredentialsModel.username && userCredentialsModel.password){
                router.navigate('timeline', {trigger: true});
                return false
            }
            var template = _.template($("#login-template").html(), {});
            var footerTemplate = _.template($("#footer-template").html(), {});
            this.$el.html(template);
            this.$el.append(footerTemplate);
        }
    });
    var loginView = new LoginView();

    /* timeline of various feedbacks */
    var FeedbackTimelineView = Backbone.View.extend({
        el: '.main-app',
        events: {
            'click ul.feedback-timeline li.row': 'showCustomerDetails',
        },
        showCustomerDetails: function(ev){
            var feedbackID = $(ev.currentTarget).find("input[type=hidden]")[0].value;
            var feedback = feedbackTimelineCollection.get(feedbackID);
            var template = _.template($("#timeline-customer-details-template").html(), {feedback: feedback});
            var toRemoveClass = $("li.row.selected").removeClass("selected"); // remove already existng 'selected' class
            $(ev.currentTarget).addClass("selected"); // add 'selected' class to clicked li element
            var toAppendTo = $(ev.currentTarget.parentElement.parentElement.parentElement); // element to append details
            var toRemove = $("aside[id=details]") // already existing details to remove
            if (toRemove){
                toRemove.remove();
            }
            toAppendTo.append(template);
        },
        render: function(){
            if (!userCredentialsModel.username && !userCredentialsModel.password){
                router.navigate('', {trigger: true});
                return
            }
            var that = this;
            // fetching feedback timeline
            feedbackTimelineCollection = new FeedbackTimelineCollection();
            feedbackTimelineCollection.credentials = {
                username: userCredentialsModel.username,
                password: userCredentialsModel.password
            };
            feedbackTimelineCollection.fetch({
                success: function(feedbacks){
                    var template = _.template($("#feedback-timeline-template").html(), {feedbacks: feedbacks.models});
                    var headerTemplate = _.template($("#header-template").html(), {username: userCredentialsModel.username});
                    var footerTemplate = _.template($("#footer-template").html(), {});
                    that.$el.html(template);
                    that.$el.prepend(headerTemplate);
                    that.$el.append(footerTemplate);
                    $(document).foundation(); 
                }
            });
        }
    });
    var feedbackTimelineView = new FeedbackTimelineView();

    /* view of list of feedbacks */
    var FeedbackFormsView = Backbone.View.extend({
        el: '.main-app',
        events: {
            'click ul.forms-list li.row': 'showFormInstances',
        },
        showFormInstances: function(ev){
            var formID = $(ev.currentTarget).find("input[type=hidden]")[0].value;
            formInstancesCollection = new FormInstancesCollection({id: formID});
            formInstancesCollection.credentials = {
                username: userCredentialsModel.username,
                password: userCredentialsModel.password
            };
            formInstancesCollection.fetch({
                success: function(instances){
                    var template =  _.template($("#form-instances-side-list-template").html(), {instances: instances.models, form_id: formID});
                    var toAppendTo = $(ev.currentTarget.parentElement.parentElement.parentElement); // element to append details
                    var toRemoveClass = $("li.row.selected").removeClass("selected"); // remove already existng 'selected' class
                    $(ev.currentTarget).addClass("selected"); // add 'selected' class to clicked li element
                    var toRemove = $("#form-instances-side-list") // already existing instance list to remove
                    if (toRemove){
                        toRemove.remove();
                    }
                    toAppendTo.append(template);
                },    
            });
        },
        render: function(){
            if (!userCredentialsModel.username && !userCredentialsModel.password){
                router.navigate('', {trigger: true});
                return
            }
            var that = this;
            feedbackFormsCollection = new FeedbackFormsCollection();
            feedbackFormsCollection.credentials = {
                username: userCredentialsModel.username,
                password: userCredentialsModel.password
            };
            feedbackFormsCollection.fetch({
                success: function(forms){
                    var template = _.template($("#feedback-forms-list-template").html(), {forms: forms.models});
                    var headerTemplate = _.template($("#header-template").html(), {username: userCredentialsModel.username});
                    var footerTemplate = _.template($("#footer-template").html(), {});
                    that.$el.html(template);
                    that.$el.prepend(headerTemplate);
                    that.$el.append(footerTemplate);
                }
            });
        }
    });
    var feedbackFormsView = new FeedbackFormsView();

    /* list of instances attached to a feedback form */
    var FeedbackFormInstancesView = Backbone.View.extend({
        el: '.main-app',
        render: function(options){
            if (!userCredentialsModel.username && !userCredentialsModel.password){
                router.navigate('', {trigger: true});
                return
            }
            var that = this;
            var form = new FormModel({id: options.formID});
            form.credentials = {
                username: userCredentialsModel.username,
                password: userCredentialsModel.password
            };
            form.fetch({
                success: function(){
                    formInstancesCollection = new FormInstancesCollection({id: options.formID});
                    formInstancesCollection.credentials = {
                        username: userCredentialsModel.username,
                        password: userCredentialsModel.password
                    };
                    formInstancesCollection.fetch({
                        success: function(instances){
                            var template = _.template($("#form-instances-list-template").html(), {instances: instances.models, form: form});
                            var headerTemplate = _.template($("#header-template").html(), {username: userCredentialsModel.username});
                            var footerTemplate = _.template($("#footer-template").html(), {});
                            that.$el.html(template);
                            that.$el.prepend(headerTemplate);
                            that.$el.append(footerTemplate);
                        }    
                    });
                }   
            });
        }
    });
    var feedbackFormInstancesView = new FeedbackFormInstancesView();

    /* view for creation of feedback */
    var FeedbackFormCreationView = Backbone.View.extend({
        el: '.main-app',
        events: {
            'submit #form-form': 'createNewForm',
        },
        createNewForm: function(ev){
            ev.preventDefault();
            var formDetails = $(ev.currentTarget).serializeObject();
            var form = new FormModel();
            form.credentials = {
                username: userCredentialsModel.username,
                password: userCredentialsModel.password
            };
            form.save(formDetails, {
                success: function(form){
                    router.navigate('/feedback_forms', {trigger: true});
                    return;
                }
            });
        },
        render: function(){
            if (!userCredentialsModel.username && !userCredentialsModel.password){
                router.navigate('', {trigger: true});
                return
            }
            var template = _.template($("#form-creation-form-template").html(), {});
            var headerTemplate = _.template($("#header-template").html(), {username: userCredentialsModel.username});
            var footerTemplate = _.template($("#footer-template").html(), {});
            this.$el.html(template);
            this.$el.prepend(headerTemplate);
            this.$el.append(footerTemplate);
        }
    });
    var feedbackFormCreationView = new FeedbackFormCreationView();

    /* view for creation of a new instance attached to a form */
    var NewInstanceCreationView = Backbone.View.extend({
        el: '.main-app',
        events: {
            'submit #instances-form': 'createNewInstance'
        },
        createNewInstance: function(ev){
            ev.preventDefault();
            var instanceDetails = $(ev.currentTarget).serializeObject();
            var instance = new InstanceModel({form_id: instanceDetails.form_id});
            instance.credentials = {
                username: userCredentialsModel.username,
                password: userCredentialsModel.password
            };
            instance.save(instanceDetails, {
                success: function(instance){
                    router.navigate('/feedback_forms/' + instanceDetails.form_id + '/instances', {trigger: true});
                    return
                }    
            });
            console.log(instanceDetails);
        },
        render: function(options){
            if (!userCredentialsModel.username && !userCredentialsModel.password){
                router.navigate('', {trigger: true});
                return
            }
            var that = this;
            var form = new FormModel({id: options.formID});
            form.credentials = {
                username: userCredentialsModel.username,
                password: userCredentialsModel.password
            };
            form.fetch({
                success: function(form){
                    var template = _.template($("#instance-creation-form-template").html(), {form: form});
                    var headerTemplate = _.template($("#header-template").html(), {username: userCredentialsModel.username});
                    var footerTemplate = _.template($("#footer-template").html(), {});
                    that.$el.html(template);
                    that.$el.prepend(headerTemplate);
                    that.$el.append(footerTemplate);
                }    
            });
        }
    });
    var newInstanceCreationView = new NewInstanceCreationView();

    var router = new Router();
    
    router.on('route:login', function(){
        loginView.render();
    });

    router.on('route:feedbackTimeline', function(){
        feedbackTimelineView.render();
    });

    router.on('route:feedbackForms', function(){
        feedbackFormsView.render();
    });

    router.on('route:formInstancesList', function(form_id){
        feedbackFormInstancesView.render({formID: form_id});
    });

    router.on('route:newFeedbackForm', function(){
        feedbackFormCreationView.render();
    });

    router.on('route:newFormInstances', function(form_id){
        newInstanceCreationView.render({formID: form_id});
    });

    Backbone.history.start();
});
