// Filename: main.js

require.config({

    'paths': {
        'jquery': 'libs/jquery',
        'underscore': 'libs/underscore',
        'backbone': 'libs/backbone',
        'jquery.fullPage': 'libs/jquery.fullPage'
    },

    'shim': {
        'jquery.fullPage': ['jquery']
    }

});

require(['App'], function(App){
    App.initialize();
});
