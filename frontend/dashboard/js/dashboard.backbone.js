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

    /* method to download a file on a URL using the iFrame trick */
    var downloadURL = function downloadURL(url) {
        var hiddenIFrameID = 'hiddenDownloader',
            iframe = document.getElementById(hiddenIFrameID);
        if (iframe === null) {
            iframe = document.createElement('iframe');
            iframe.id = hiddenIFrameID;
            iframe.style.display = 'none';
            document.body.appendChild(iframe);
        }
        iframe.src = url;
    };

	/* hostname of the api */
	var api_root = 'https://ingage-staging-1.herokuapp.com'

    /* logs out the user on the click of the logout link */
    logoutUser = function(ev){
        ev.preventDefault();
        $.removeCookie("username");
        $.removeCookie("password");
        router.navigate('', {trigger: true})
        return false
    }

    /* feedback timeline feedback model */
    var FeedbackModel = Backbone.Model.extend({});

    /* collection storing the list of feedbacks which come in the timeline */
    var FeedbackTimelineCollection = Backbone.Collection.extend({
        model: FeedbackModel,
        initialize: function(nps_score_start, nps_score_end, start_date, end_date){
            this.nps_score_start = nps_score_start;
            this.nps_score_end = nps_score_end;
            this.start_date = start_date;
            this.end_date = end_date;
        },
        urlRoot: function(){
            params = {}
            var that = this;
            if (this.nps_score_start && this.nps_score_end){
                params['nps_score_start'] = that.nps_score_start;
                params['nps_score_end'] = that.nps_score_end;
            }
            if (this.start_date && this.end_date){
                params['start_date'] = that.start_date.format('YYYY-MM-DD').replace("00", "20");
                params['end_date'] = that.end_date.format('YYYY-MM-DD').replace("00", "20");
            }
            return api_root + "/dashboard/timeline?" + $.param(params)
        },
        parse: function(response, xhr){
            // set the total number of items for pagination
            this.actAs_Paginatable_totalItems = response.total_results;
            this.start_date = moment(response.start_date);
            this.end_date = moment(response.end_date);
            this.all_start_date = moment(response.all_start_date);
            this.all_end_date = moment(response.all_end_date);
            return response.feedbacks;
        }
    });
    Backbone.actAs.Paginatable.init(FeedbackTimelineCollection, FeedbackModel);

    /* collection of the list of feedback forms of the merchant */
    var FeedbackFormsCollection = Backbone.Collection.extend({
        url: api_root + "/dashboard/forms",
        parse: function(response, xhr){
            return response.forms;
        }
    });

    /* collection of instances of a form */
    FormInstancesCollection = Backbone.Collection.extend({
        initialize: function(options){
            this.id = options.id;
        },
        url: function(){
            return api_root + "/dashboard/forms/" + this.id + "/instances"
        },
        parse: function(response, xhr){
            return response.instances 
        }
    });
    
    /* model of the feedback form */
    var FormModel = Backbone.Model.extend({
        urlRoot: api_root + "/dashboard/forms",
        parse: function(response, xhr){
            return response.form
        }
    });

    /* model for sign up requests */
    SignupRequestModel = Backbone.Model.extend({
        urlRoot: api_root + "/dashboard/signup_request"
    });

    /* model of the instance attached to the feedback form */
    InstanceModel = Backbone.Model.extend({
        initialize: function(props){
            this.form_id = props.form_id;
        },
        urlRoot: function(){
            return api_root + "/dashboard/forms/" + this.form_id + "/instances"
        }
    });

    /* model storing the analytics of the form */
    FormAnalyticsModel = Backbone.Model.extend({
        initialize: function(props){
            this.instance_ids = props.instance_ids;
            this.form_id = props.form_id;
            this.start_date = props.start_date;
            this.end_date = props.end_date;
        },
        urlRoot: function(){
            return api_root + '/dashboard/forms/' + this.form_id + '/analytics?instance_ids=' + this.instance_ids + 
                                '&start_date=' + this.start_date + '&end_date=' + this.end_date
        }
    });


    /* login page */
    var LoginView = Backbone.View.extend({
        el: '.main-app',
        events: {
            'submit #login-form': 'loginUser',
            'click #load-signup, #contact-signup': 'showSignup',
            'click #signup-center' : 'focusSignup',
            'submit #signup-form': 'sendSignupRequest'
        },
        sendSignupRequest: function(ev){
            ev.preventDefault();
            var customerDetails = $(ev.currentTarget).serializeObject();
            var signupRequestModel = new SignupRequestModel();
            signupRequestModel.save(customerDetails, {
                success: function(data){
                    //TODO: show the feeedback to the user properly
                    $("#signup-submit").fadeOut(300);
                    $("#signup-confirm").delay(300).fadeIn(300);
                }
            });
        },
        showSignup: function(ev){
            ev.preventDefault();
            $('#login-form').fadeOut(300);
            $('#load-signup').fadeOut(300);
            $('#signup-form').delay(300).fadeIn(300);
        },
        focusSignup: function(ev){
            ev.preventDefault();
            $("html, body").animate({ scrollTop: 0 }, "slow");
            $('#login-form').fadeOut(300);
            $('#load-signup').fadeOut(300);
            $('#signup-form').delay(300).fadeIn(300);
            $('.login-container').addClass('shake');
        },
        loginUser: function(ev){
            ev.preventDefault();
            var credentials = $(ev.currentTarget).serializeObject();
            var submitButton = $('#login-submit');              // Variable to cache button element
            var loadingButton= $('.loading');
            var errorBox= $('.error');
            var alertBox = $('.alert-box');                 // Variable to cache meter element
            $(submitButton).fadeOut(300); 
            $(loadingButton).delay(300).fadeIn(300); 
            $.ajax({
                type: "GET",
                url: api_root + "/dashboard/auth/check_credentials",
                headers: Backbone.BasicAuth.getHeader({ username: credentials.username, password: credentials.password }),
                success: function(data){
                    $.cookie("username", credentials.username);
                    $.cookie("password", credentials.password);
                    router.navigate('timeline', {trigger: true});
                },
                error: function(data){
                    $(loadingButton).fadeOut(300); 
                    $(submitButton).delay(300).fadeIn(300); 
                    $(errorBox).fadeIn(300);
                    $( "input" ).click(function() {
                        $(errorBox).fadeOut(300);
                    });
                } 
            });
        },
        render: function(){
            if ($.cookie("username") && $.cookie("password")){
                router.navigate('timeline', {trigger: true});
                return false
            }

            // change the title
            document.title = "Ingage: Your in-venue Customer Experience Management system";

            $('.main-app').addClass('home');

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
            'click #logout-link': logoutUser,
            'click #timeline-refresh-button': 'refreshTimeline',
            'click .nps-score-filter li a': 'npsScoreFilter',
            'click .pagination li a': 'changePageTimeline',
            'click .form-filter li': 'exportCSV',
        },
        exportCSV: function(ev){
            ev.preventDefault();
            var formID = $(ev.currentTarget).find("a").attr("data-id");
            params = {}
            if (this.nps_score_start && this.nps_score_end){
                params['nps_score_start'] = this.nps_score_start;
                params['nps_score_end'] = this.nps_score_end;
            }
            params['start_date'] = feedbackTimelineCollection.start_date.format('YYYY-MM-DD');
            params['end_date'] = feedbackTimelineCollection.end_date.format('YYYY-MM-DD');
            params['form_id'] = formID;
            $.ajax({
                'method': 'GET',
                'url': api_root + '/dashboard/timeline/csv_export?' + $.param(params),
                'headers': Backbone.BasicAuth.getHeader({ username: $.cookie("username"), password: $.cookie("password") }),
                'success': function(data){
                    downloadURL(data['csv_url']);
                    return;
                }
            })
        },
        changePageTimeline: function(ev){
            ev.preventDefault();
            var target = $(ev.currentTarget);
            var pageNumber = target.text();
            this.current_page = Number(pageNumber);
            this.render()
        },
        npsScoreFilter: function(ev){
            ev.preventDefault();
            var target = $(ev.currentTarget);
            var that = this;
            this.current_page = null;
            if (target.hasClass("promoters")) {
                that.nps_score_start = 9;
                that.nps_score_end = 10;
            } else if (target.hasClass("passive")) {
                that.nps_score_start = 7;
                this.nps_score_end = 8;
            } else {
                that.nps_score_start = 1;
                that.nps_score_end = 6;
            }
            this.render()
        },
        refreshTimeline: function(ev){
            this.current_page = null;
            this.render();
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
            if (!$.cookie("username") && !$.cookie("password")){
                router.navigate('', {trigger: true});
                return
            }

            // change the title
            document.title = "Feedback Timeline | Ingage Dashboard";

            // fetching feedback timeline
            var that = this;
            feedbackTimelineCollection = new FeedbackTimelineCollection(this.nps_score_start, this.nps_score_end, 
                                    this.startDateRangePicker, this.endDateRangePicker);

            // pagination properties of the collection
            currentPage = this.current_page || 1;
            feedbackTimelineCollection.actAs_Paginatable_currentPage_attr = "page";
            feedbackTimelineCollection.actAs_Paginatable_itemsPerPage_attr = "rpp";
            feedbackTimelineCollection.currentPage(currentPage);
            feedbackTimelineCollection.itemsPerPage(20);

            // basic auth credentials
            feedbackTimelineCollection.credentials = {
                username: $.cookie("username"),
                password: $.cookie("password")
            };

            // fetch the timeline from the server
            feedbackTimelineCollection.fetch({
                async:false,
                success: function(feedbacks){

                    // pages numbers (for navigation in timeline) to show in the templates
                    paginationInfo = feedbacks.paginationInfo();
                    pagesToShow = [];
                    leftSide = _.range(1, paginationInfo.currentPage);
                    rightSide = _.range(paginationInfo.currentPage+1, paginationInfo.totalPages+1);
                    for (var i=0; i < leftSide.length; i++){
                        pagesToShow.push(leftSide[i]);
                    }
                    pagesToShow.push(paginationInfo.currentPage);
                    for (var i=0; i<rightSide.length; i++){
                        pagesToShow.push(rightSide[i]);
                    }

                    feedbackFormsCollection = new FeedbackFormsCollection();
                    feedbackFormsCollection.credentials = {
                        username: $.cookie("username"),
                        password: $.cookie("password")
                    };
                    feedbackFormsCollection.fetch({
                        'async': false,
                        'success': function(forms){
                            // mumbo jumbo of templates
                            var template = _.template($("#feedback-timeline-template").html(),
                                {feedbacks: feedbacks.models, pagesToShow: pagesToShow,
                                    currentPage: paginationInfo.currentPage, forms: forms.models});
                            var headerTemplate = _.template($("#header-template").html(), {username: $.cookie("username")});
                            var footerTemplate = _.template($("#footer-template").html(), {});
                            that.$el.html(template);
                            that.$el.prepend(headerTemplate);
                            that.$el.append(footerTemplate);
                        }
                    })

                    // jquery shit
                    $(document).foundation(); 
                    $(window).scroll(function() {
				        var scroll = $(window).scrollTop();
				        if (scroll >= 550) {
				            $("#details .panel").addClass("stickit");
				        } else {
				            $("#details .panel").removeClass("stickit");
				        }
				    });

                    this.startDateRangePicker = feedbackTimelineCollection.start_date;
                    this.endDateRangePicker = feedbackTimelineCollection.end_date;
                    minDate = feedbackTimelineCollection.all_start_date;
                    maxDate = feedbackTimelineCollection.all_end_date;
                    $('#reportrange').daterangepicker({
                        startDate: this.startDateRangePicker.format('MM-DD-YYYY'),
                        endDate: this.endDateRangePicker.format('MM-DD-YYYY'),
                        minDate: minDate.format('MM-DD-YYYY'),
                        maxDate: maxDate.format('MM-DD-YYYY'),
                        dateLimit: { days: 60 },
                        showDropdowns: true,
                        showWeekNumbers: false,
                        timePicker: false,
                        timePickerIncrement: 1,
                        timePicker12Hour: true,
                        ranges: {
                        'Today': [moment(), moment()],
                        'Yesterday': [moment().subtract('days', 1), moment().subtract('days', 1)],
                        'Last 7 Days': [moment().subtract('days', 6), moment()],
                        'Last 30 Days': [moment().subtract('days', 29), moment()],
                        'This Month': [moment().startOf('month'), moment()],
                        'Last Month': [moment().subtract('month', 1).startOf('month'), moment().subtract('month', 1).endOf('month')],
                        'This Year': [moment().startOf('year'), moment()]
                        },
                        opens: 'left',
                        format: 'MM/DD/YYYY',
                        separator: ' to ',
                        locale: {
                            applyLabel: 'Submit',
                            fromLabel: 'From',
                            toLabel: 'To',
                            customRangeLabel: 'Custom Range',
                            daysOfWeek: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr','Sa'],
                            monthNames: ['January', 'February', 'March', 'April', 'May',
                                'June', 'July', 'August', 'September', 'October', 'November', 'December'],
                            firstDay: 1
                        }
                    },
                        function(start, end) {
                            that.current_page = null;
                            tat = start;
                            that.startDateRangePicker = start;
                            that.endDateRangePicker = end;
                            $('#reportrange span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
                            that.render()
                        }
                    );
                    //Set the initial state of the picker label
                    $('#reportrange span').html(this.startDateRangePicker.format('MMMM D, YYYY') + ' - ' +
                            this.endDateRangePicker.format('MMMM D, YYYY'));
                }
            });
            $('#selectall').click(function(event) {  //on click 
                if(this.checked) { // check select status
                    $('.chkb').each(function() { //loop through each checkbox
                        this.checked = true;  //select all checkboxes with class "checkbox1"               
                    });
                }else{
                    $('.chkb').each(function() { //loop through each checkbox
                        this.checked = false; //deselect all checkboxes with class "checkbox1"                       
                    });         
                }
            });            
        }
    });
    feedbackTimelineView = new FeedbackTimelineView();

    /* Analytics View */
    var AnalyticsView = Backbone.View.extend({
        el: '.main-app',
        events: {
            'click #logout-link': logoutUser,
            'change .form-change select': 'changeForm',
            'click .question-list li': 'changeFormFieldAnalytics'
        },
        changeFormFieldAnalytics: function(ev){
            field_id = $(ev.currentTarget).attr('id');
            this.changeForm(ev=false, field_id=field_id);
        },
        donutScript: function(fieldAnalytics){
            data = [];
            for (i in fieldAnalytics.numbers){
                data.push({
                    value: fieldAnalytics.numbers[i].number,
                    color: fieldAnalytics.numbers[i].color
                });
            }
            var doughnutData0 = data;
            var myDoughnut0 = new Chart(document.getElementById("canvas0").getContext("2d")).Doughnut(doughnutData0,{
                labelAlign: 'center'
            });
        
        },
        changeForm: function(ev, field_id){
            start_date = startDateRangePicker.format("YYYY-MM-DD");
            end_date = endDateRangePicker.format("YYYY-MM-DD");
            if (ev){
                formID = $(ev.currentTarget).find(":selected").attr("id");
                formName = $(ev.currentTarget).find(":selected").val();
            } else {
                formID = $('input[name="form_id"]').val();
                formName = $('input[name="form_name"]').val();
            }
            formInstancesCollection = new FormInstancesCollection({id: formID});
            formInstancesCollection.credentials = {
                username: $.cookie("username"),
                password: $.cookie("password")
            };
            var that = this;
            formInstancesCollection.fetch({
                success: function(instances){
                    instanceIDs = '';
                    for (i in instances.models){
                        if (i == 0){
                            instanceIDs = instanceIDs + instances.models[i].id;
                        } else {
                            instanceIDs = instanceIDs + ',' + instances.models[i].id;
                        }
                    }
                    analyticsModel = new FormAnalyticsModel({form_id: formID, instance_ids: instanceIDs, start_date: start_date,
                                                                end_date: end_date});
                    analyticsModel.credentials = {
                        username: $.cookie("username"),
                        password: $.cookie("password")
                    };
                    analyticsModel.fetch({
                        success: function(analytics){
                            if (analytics.attributes.no_analytics){
                                var template = _.template($("#analytics-do-not-exist-template").html());
                                $("#form-analytics").replaceWith(template);
                                return
                            }
                            if (!field_id){
                                fieldAnalytics = analytics.attributes.analytics[0];
                            } else {
                                for (i in analytics.attributes.analytics){
                                    if (analytics.attributes.analytics[i].field.id == field_id){
                                        fieldAnalytics = analytics.attributes.analytics[i];
                                    }    
                                }
                            }
                            var template = _.template($("#analytics-template").html(), {analyticsExist: true, 
                                analytics: analytics, field_analytics: fieldAnalytics, form_id: formID, form_name: formName});
                            $("#form-analytics").replaceWith(template);
                            that.donutScript(fieldAnalytics);
                        }
                    });
                }
            });
        },
        render: function(){
            if (!$.cookie("username") && !$.cookie("password")){
                router.navigate('', {trigger: true});
                return
            }

            // change the title
            document.title = "Feedback Timeline | Ingage Dashboard";

            // fetch feedback forms
            feedbackFormsCollection = new FeedbackFormsCollection();
            feedbackFormsCollection.credentials = {
                username: $.cookie("username"),
                password: $.cookie("password")
            };
            var that = this;
            feedbackFormsCollection.fetch({
                async: false,
                success: function(forms){
                var template = _.template($("#analytics-choose-template").html(), {analyticsExist: false});
                var settingstemplate = _.template($("#analytics-settings-template").html(), {forms: forms.models});
                var headerTemplate = _.template($("#header-template").html(), {username: $.cookie("username")});
                var footerTemplate = _.template($("#footer-template").html(), {});
                that.$el.html(settingstemplate);
                that.$el.append(template);
                that.$el.prepend(headerTemplate);
                that.$el.append(footerTemplate);
                startDateRangePicker = moment().subtract('days', 29);
                endDateRangePicker = moment();
                $('#reportrange').daterangepicker({
                    startDate: startDateRangePicker,
                    endDate: endDateRangePicker,
                    minDate: '01/01/2012',
                    maxDate: '12/31/2014',
                    dateLimit: { days: 60 },
                    showDropdowns: true,
                    showWeekNumbers: false,
                    timePicker: false,
                    timePickerIncrement: 1,
                    timePicker12Hour: true,
                    ranges: {
                    'Today': [moment(), moment()],
                    'Yesterday': [moment().subtract('days', 1), moment().subtract('days', 1)],
                    'Last 7 Days': [moment().subtract('days', 6), moment()],
                    'Last 30 Days': [moment().subtract('days', 29), moment()],
                    'This Month': [moment().startOf('month'), moment()],
                    'Last Month': [moment().subtract('month', 1).startOf('month'), moment().subtract('month', 1).endOf('month')],
                    'This Year': [moment().startOf('year'), moment()]
                    },
                    opens: 'left',
                    format: 'MM/DD/YYYY',
                    separator: ' to ',
                    locale: {
                        applyLabel: 'Submit',
                        fromLabel: 'From',
                        toLabel: 'To',
                        customRangeLabel: 'Custom Range',
                        daysOfWeek: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr','Sa'],
                        monthNames: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
                        firstDay: 1
                    }
                },
                function(start, end) {
                    startDateRangePicker = start;
                    endDateRangePicker = end;
                    var field_id = $("li.active").attr("id");
                    if ($("input[name='form_id']")){
                        that.changeForm(ev=false, field_id=field_id);
                    }
                    $('#reportrange span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
                }
		  );
		  //Set the initial state of the picker label
		  $('#reportrange span').html(moment().subtract('days', 29).format('MMMM D, YYYY') + ' - ' + moment().format('MMMM D, YYYY'));
                }
            });
        }
    });
    var AnalyticsView = new AnalyticsView();


    /* view of list of feedbacks */
    var FeedbackFormsView = Backbone.View.extend({
        el: '.main-app',
        events: {
            'click ul.forms-list li.row': 'showFormInstances',
            'click #logout-link': logoutUser
        },
        showFormInstances: function(ev){
            var formID = $(ev.currentTarget).find("input[type=hidden]")[0].value;
            formInstancesCollection = new FormInstancesCollection({id: formID});
            formInstancesCollection.credentials = {
                username: $.cookie("username"),
                password: $.cookie("password")
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
            if (!$.cookie("username") && !$.cookie("password")){
                router.navigate('', {trigger: true});
                return
            }

            // change the title
            document.title = "All Forms | Ingage Dashboard";

            var that = this;
            feedbackFormsCollection = new FeedbackFormsCollection();
            feedbackFormsCollection.credentials = {
                username: $.cookie("username"),
                password: $.cookie("password")
            };
            feedbackFormsCollection.fetch({
                async: false,
                success: function(forms){
                    var template = _.template($("#feedback-forms-list-template").html(), {forms: forms.models});
                    var headerTemplate = _.template($("#header-template").html(), {username: $.cookie("username")});
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
        events: {
            'click #logout-link': logoutUser
        },
        render: function(options){
            if (!$.cookie("username") && !$.cookie("password")){
                router.navigate('', {trigger: true});
                return
            }

            // change the title
            document.title = "All Instances | Ingage Dashboard";

            var that = this;
            var form = new FormModel({id: options.formID});
            form.credentials = {
                username: $.cookie('username'),
                password: $.cookie('password')
            };
            form.fetch({
                success: function(){
                    formInstancesCollection = new FormInstancesCollection({id: options.formID});
                    formInstancesCollection.credentials = {
                        username: $.cookie('username'),
                        password: $.cookie('password')
                    };
                    formInstancesCollection.fetch({
                        success: function(instances){
                            var template = _.template($("#form-instances-list-template").html(),
                                {instances: instances.models, form: form});
                            var headerTemplate = _.template($("#header-template").html(), {username: $.cookie('username')});
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

    var FeedbackFormCreationView = Backbone.View.extend({
        el: '.main-app',
        events: {
            'submit #form-form': 'createNewForm',
            'click #logout-link': logoutUser
        },
        createNewForm: function(ev){
            ev.preventDefault();
            var formDetails = $(ev.currentTarget).serializeObject();
            var form = new FormModel();
            form.credentials = {
                username: $.cookie("username"),
                password: $.cookie("password")
            };
            form.save(formDetails, {
                success: function(form){
                    router.navigate('/feedback_forms', {trigger: true});
                    return;
                }
            });
        },
        render: function(){
            if (!$.cookie("username") && !$.cookie("password")){
                router.navigate('', {trigger: true});
                return
            }

            // change the title
            document.title = "Create a Form | Ingage Dashboard";

            var template = _.template($("#form-creation-form-template").html(), {});
            var headerTemplate = _.template($("#header-template").html(), {username: $.cookie('username')});
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
            'submit #instances-form': 'createNewInstance',
            'click #logout-link': logoutUser
        },
        createNewInstance: function(ev){
            ev.preventDefault();
            var instanceDetails = $(ev.currentTarget).serializeObject();
            var instance = new InstanceModel({form_id: instanceDetails.form_id});
            instance.credentials = {
                username: $.cookie("username"),
                password: $.cookie("username")
            };
            instance.save(instanceDetails, {
                success: function(instance){
                    router.navigate('/feedback_forms/' + instanceDetails.form_id + '/instances', {trigger: true});
                    return
                }    
            });
        },
        render: function(options){
            if (!$.cookie("username") && !$.cookie("password")){
                router.navigate('', {trigger: true});
                return
            }
            
            // change the title
            document.title = "Create an Instance | Ingage Dashboard";

            var that = this;
            var form = new FormModel({id: options.formID});
            form.credentials = {
                username: $.cookie("username"),
                password: $.cookie("password")
            };
            form.fetch({
                success: function(form){
                    var template = _.template($("#instance-creation-form-template").html(), {form: form});
                    var headerTemplate = _.template($("#header-template").html(), {username: $.cookie("username")});
                    var footerTemplate = _.template($("#footer-template").html(), {});
                    that.$el.html(template);
                    that.$el.prepend(headerTemplate);
                    that.$el.append(footerTemplate);
                }    
            });
        }
    });
    var newInstanceCreationView = new NewInstanceCreationView();

    /* all the routes of the merchant dashboard */
    var Router = Backbone.Router.extend({
        routes: {
            "": "login",
            "timeline": "feedbackTimeline",
            "feedback_forms": "feedbackForms",
            "feedback_forms/new": "newFeedbackForm",
            "feedback_forms/:form_id/instances": "formInstancesList",
            "feedback_forms/:form_id/instances/new": "newFormInstances",
            "analytics": "analytics",
        },
    });

    var highlightNavLinks = function(route){
        var selector = $("#nav-" + route);
        if (!selector.hasClass("active")){
            $(".top-bar-secion .active").removeClass("active");
            $(selector).addClass("active");
        }
    };

    router = new Router();

    router.on('route:login', function(){
        loginView.render();
    });

    router.on('route:feedbackTimeline', function(){
        feedbackTimelineView.render();
        highlightNavLinks("timeline");
    });

    router.on('route:analytics', function(){
        AnalyticsView.render();
        highlightNavLinks("analytics");
    });

    router.on('route:feedbackForms', function(){
        feedbackFormsView.render();
        highlightNavLinks("feedback_forms");
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
