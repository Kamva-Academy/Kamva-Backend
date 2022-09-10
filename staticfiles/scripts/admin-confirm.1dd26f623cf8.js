var didSet = false;
console.log('here');
setInterval(
	function() {
		(function($) {
			$(document).ready(function(){
				if (!didSet) {
				    $('.unset-all-current-states').click(function() {
				        var c = confirm("Continue unsettings? This action is irreversible!");
				        return c;
				    });
				    didSet = true;
				}
			})
		})(django.jQuery)
	}, 400
)