requirejs.config({
  'baseUrl': '/ingaged/frontend',
  'paths': {
    'app': 'customer/js',
    // define vendor paths
    'jquery': 'js/vendor/jquery-2.0.3.min',
    'underscore': 'js/vendor/underscore-min',
    'backbone': 'js/vendor/backbone-min',
  },
   'shim': {
    'underscore': {
      'exports': '_'
    },
    'backbone': {
      'deps': ['jquery', 'underscore'],
      'exports': 'Backbone'
    },
  }
});