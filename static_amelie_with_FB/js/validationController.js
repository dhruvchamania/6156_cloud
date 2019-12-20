
angular.module('CustomerApp',[]).controller("validationController",
    function ($scope, $http){
        $scope.submitAddress=function(){
            var address=$scope.fields;
            var req = {
                method: 'POST',
                url: 'https://hm88roi4i8.execute-api.us-east-1.amazonaws.com/dev/address-val',
                headers: {'Content-Type': "application/json", 'Access-Control-Allow-Origin': "*"},
                data: address
            };

            $http(req).then(function successCallback(response) {console.log(response);}, function errorCallback(response)
                {console.log(response);});

    };

});
