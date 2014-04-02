// Filename: main.js

require.config({

    paths: {
        jquery: 'libs/jquery',
        underscore: 'libs/underscore',
        backbone: 'libs/backbone'
    },

});

require(['app'], function(App){
    App.initialize();
});
