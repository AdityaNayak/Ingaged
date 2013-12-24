/**
For all other js things on the dashbard
**/

$(document).ready(function() {
    $(window).scroll(function() {
        var scroll = $(window).scrollTop();
        if (scroll >= 200) {
            $("#details").addClass("stickit");
        } else {
            $("#details").removeClass("stickit");
        }
    });
    $(function(){
    $(".top-bar-section ul li>a").click(function(){ //
    	$("#loading-bar").fadeIn(300);
   		});
	});
    $('#reportrange').daterangepicker({
        startDate: moment().subtract('days', 29),
        endDate: moment(),
        minDate: '01/01/2012',
        maxDate: '12/31/2014',
        dateLimit: { days: 60 },
        showDropdowns: true,
        showWeekNumbers: false,
        timePicker: false,
        timePickerIncrement: 1,
        timePicker12Hour: true,
        ranges: {
           'Today': [moment(), moment()],
           'Yesterday': [moment().subtract('days', 1), moment().subtract('days', 1)],
           'Last 7 Days': [moment().subtract('days', 6), moment()],
           'Last 30 Days': [moment().subtract('days', 29), moment()],
           'This Month': [moment().startOf('month'), moment()],
           'Last Month': [moment().subtract('month', 1).startOf('month'), moment().subtract('month', 1).endOf('month')],
           'This Year': [moment().startOf('year'), moment()]
        },
        opens: 'left',
        format: 'MM/DD/YYYY',
        separator: ' to ',
        locale: {
            applyLabel: 'Submit',
            fromLabel: 'From',
            toLabel: 'To',
            customRangeLabel: 'Custom Range',
            daysOfWeek: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr','Sa'],
            monthNames: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
            firstDay: 1
        }
     },
     function(start, end) {
      console.log("Callback has been called!");
      $('#reportrange span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
     }
  );
  //Set the initial state of the picker label
  $('#reportrange span').html(moment().subtract('days', 29).format('MMMM D, YYYY') + ' - ' + moment().format('MMMM D, YYYY'));
});
