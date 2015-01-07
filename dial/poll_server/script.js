
var module = angular.module('vis', [])
	.directive('onFinishRender', function ($timeout) {
    return {
        restrict: 'A',
        link: function (scope, element, attr) {
            if (scope.$last === true) {
                $timeout(function () {
                    scope.$emit('ngRepeatFinished');
                });
            }
        }
    }
});



module.controller('angControl', ['$scope', '$http',
  function($scope,$http) {
  	//$scope.sensor_value = 0;
  	$scope.theme_word = 'weather';
  	$scope.sensor_value = '200';
  	(function poll(){
	    setTimeout(function() {		
		$.ajax({ 
		    url: "http://192.168.0.1/pollserver/longPoll.php",
		    type: "GET",
		    async: false,
		    success: function(data) {
			if(data!=null){
			    $("#time_display").text("value at : " + new Date().getTime()+ " is "+data[0]);
			    $scope.sensor_value = data[0];
			    $("#bar").css("width",data[0]);
			}
		    }, dataType: "json",complete:poll()});
	    },50);
	})();
	    
      }
]);

