// Filename: main.js

require.config({

    paths: {
        jquery: 'libs/jquery',
        underscore: 'libs/underscore',
        backbone: 'libs/backbone'
    },

});

require(['App'], function(App){
    App.initialize();
});
