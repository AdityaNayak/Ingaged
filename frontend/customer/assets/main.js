// Filename: main.js

require.config({

    'paths': {
        'jquery': 'libs/jquery',
        'underscore': 'libs/underscore',
        'backbone': 'libs/backbone',
        'jquery.fullPage': 'libs/jquery.fullPage',
        'jquery.nouislider': 'libs/jquery.nouislider'
    },

    'shim': {
        'jquery.fullPage': ['jquery'],
        'jquery.nouislider': ['jquery']
    }

});

require(['App'], function(App){
    App.initialize();
});
