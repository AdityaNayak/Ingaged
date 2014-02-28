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

    /* api root url */
    var root_server = 'https://ingage-staging-1.herokuapp.com'

    /* all the routes of the admin panel */
    var Router = Backbone.Router.extend({
        routes: {
            "": "login",
            "merchants": "merchantList",
            "merchants/:id": "merchantView",
            "new_merchant": "newMerchant",
        }
    });

    /* collection storing the list of merchants */
    var Merchants = Backbone.Collection.extend({
        url: root_server + "/admin/merchants",
        parse: function(response, xhr){
            return response.merchants
        }
    });

    /* model for each individual merchant */
    var Merchant = Backbone.Model.extend({
        urlRoot: root_server + "/admin/merchants",
        parse: function(response, xhr){
            return response.merchant
        }
    })

    /* login form */
    var LoginView = Backbone.View.extend({
        el: '.page',
        events: {
            'submit .login-form': 'loginUser',
        },
        loginUser: function(ev){
            ev.preventDefault();
            var credentials = $(ev.currentTarget).serializeObject();
            $.ajax({
                type: "GET",
                url: root_server + "/admin/auth/check_credentials",
                headers: Backbone.BasicAuth.getHeader({ username: credentials.username, password: credentials.password }),
                success: function(data){
                    $.cookie("username", credentials.username);
                    $.cookie("password", credentials.password);
                    router.navigate('merchants', {trigger: true});
                },
                error: function(data){
                    $('.login-form .alert-error').show()
                } 
            });
        },
        render: function(){
            if ($.cookie("username") && $.cookie("password")){
                router.navigate('merchants', {trigger: true});
                return
            }
            var template = _.template($('#login-template').html(), {});
            this.$el.html(template);
        }
    });
    var loginView = new LoginView();

    /* table showing the list of all merchants existing on the platform */
    var MerchantListView = Backbone.View.extend({
        el: '.page',
        render: function(){
            if (!$.cookie("username") && !$.cookie("password")){
                router.navigate('', {trigger: true});
                return
            }
            var that = this;
            var merchants = new Merchants();
            merchants.credentials = {
                username: $.cookie("username"),
                password: $.cookie("password")
            }
            merchants.fetch({
                success: function(merchants){
                    var template = _.template($('#merchant-list-template').html(), {merchants: merchants.models});
                    that.$el.html(template);
                }    
            });
        }
    });
    var merchantListView = new MerchantListView();

    /* form showing the information of a merchant with the ability to edit the same */
    var MerchantView = Backbone.View.extend({
        el: '.page',
        events: {
            'submit .merchant-edit-form': 'saveMerchant',
            'submit .merchant-edit-file-upload': 'uploadMerchantLogo',
        },
        render: function(options){
            if (!$.cookie("username") && !$.cookie("password")){
                router.navigate('', {trigger: true});
                return
            }
            var that = this;
            var merchant = new Merchant({id: options.id});
            merchant.credentials = {
                username: $.cookie("username"),
                password: $.cookie("password")
            }
            merchant.fetch({
                success: function(merchant) {
                    var template = _.template($('#merchant-view-template').html(), {merchant: merchant});
                    that.$el.html(template);
                }   
            });
        },
        saveMerchant: function(ev){
            ev.preventDefault();
    
            // data to send to the API
            var merchantDetails = $(ev.currentTarget).serializeObject();
            if (merchantDetails['nps_notifs']) {
                merchantDetails['nps_notifs'] = true;
                merchantDetails['nps_threshold'] = Number(merchantDetails['nps_threshold']);
            } else {
                delete merchantDetails['notif_emails'];
                delete merchantDetails['nps_threshold'];
                merchantDetails['nps_notifs'] = false;
            }

            // ping the API
            var merchant = new Merchant();
            merchant.credentials = {
                username: $.cookie("username"),
                password: $.cookie("password")
            }
            merchant.save(merchantDetails, {
                success: function(merchant){
                    router.navigate('/merchants', {trigger: true})
                    return
                }
            });
        },
        uploadMerchantLogo: function(ev){
            ev.preventDefault();
            merchant_id = $(".merchant-edit-form input[name=id]").val();
            url = root_server + '/admin/merchants/' + merchant_id + '/upload_logo';
            var logo_data = new FormData();
            logo_data.append("logo", $("input[name=logo]")[0].files[0]);
            $.ajax({
                type: 'PUT',
                url: url,
                headers: Backbone.BasicAuth.getHeader({ username: $.cookie("username"), password: $.cookie("username") }),
                data: logo_data,
                processData: false,
                contentType: false,
                success: function(data){
                    router.navigate('/merchants', {trigger: true})
                    return false
                }
            });

            return
        }
    });
    var merchantView = new MerchantView();

    /* form to create a new merchant */
    var NewMerchantView = Backbone.View.extend({
        el: '.page',
        events: {
            'submit .new-merchant-form': 'newMerchant'
        },
        render: function(options){
            if (!$.cookie("username") && !$.cookie("password")){
                router.navigate('', {trigger: true});
                return
            }
            var template = _.template($('#merchant-new-template').html(), {})
            this.$el.html(template)
        },
        newMerchant: function(ev){
            var newMerchantDetails = $(ev.currentTarget).serializeObject()
            var merchant = new Merchant();
            merchant.credentials = {
                username: $.cookie("username"),
                password: $.cookie("password")
            }
            merchant.save(newMerchantDetails, {
                success: function(merchant){
                    router.navigate('/merchants', {trigger: true})
                    return
                },
                error: function(merchant){
                    $(".new-merchant-form .alert").show('slow')
                }
            });
            ev.preventDefault();
            return
        },
    });
    var newMerchantView = new NewMerchantView();

    var router = new Router()

    /* login view */
    router.on('route:login', function(){
        loginView.render();
    });

    /* view listing all merchants in a table */
    router.on('route:merchantList', function(){
        merchantListView.render();
    });

    /* view showing merchant info with ability to edit it */
    router.on('route:merchantView', function(id){
        merchantView.render({id: id});
    });

    /* view with form to create a new merchant */
    router.on('route:newMerchant', function(){
        newMerchantView.render();
    });

    Backbone.history.start();
});
