CustomerApp = angular.module('CustomerApp', [
    'ngRoute'
]);

angular.module('CustomerApp').
config(['$locationProvider', '$routeProvider',
    function config($locationProvider, $routeProvider) {
        $locationProvider.hashPrefix('!');

        console.log("In route setup.")

        $routeProvider.
        when('/', {
            templateUrl: 'index.html'
        }).
        when('static/address-validation', {
            templateUrl: 'address_validation.html'
        }).
        when('static/address-appearing', {
            templateUrl: 'address_appearing.html'
        }).
            otherwise({
            templateUrl: 'index.html'
        })
        //when('/phones/:phoneId', {
        //   template: '<phone-detail></phone-detail>'
        // })//.
        //otherwise('/home');
    }
]);
