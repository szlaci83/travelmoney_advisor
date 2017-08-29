/**
 * Created by Laszlo Szoboszlai on 26/02/2017.
 */
var HOST = 'laszloszoboszlai.me';
var PORT = '5000';
var URL = "http://" + HOST + ":" + PORT;


/*$(window).on('load',function(){
		$('#Modal').modal('show');
	});
*/

$( document ).ready(function() {
	$('#Modal').modal('show');
    var settings = {
        "async": true,
        "crossDomain": true,
        "url": URL +"/currencies",
        "method": "GET",
        "headers": {
            "cache-control": "no-cache",
            "postman-token": "43402fbd-0e3f-3d93-03ab-4f22eaf1f810"
        },
        "data": "{ \n  \"currency\" : \"EUR\",\n    \"days\": 5\n}"
    }

    $.ajax(settings).done(function (response) {
        for(var key in response){
            $('#from').append( '<li><a href="#"><id=' + key + '">' + key + '</a></li>' );
        }

            $("#from li a").click(function(){
                $("#fromDropdownMenu:first-child").text($(this).text());
                $("#fromDropdownMenu:first-child").val($(this).text());
				$("#todr").empty();
				$("#toDropdownMenu:first-child").text('Currency to');
				$("#toDropdownMenu:first-child").val('');

                var curr = ($("#fromDropdownMenu:first-child").val())
                var settings = {
					"async": true,
					"crossDomain": true,
					"url": URL+ "/tocurrencies",
					"method": "POST",
					"headers": {
						"content-type": "application/json",
						"currency": "\""  + curr + "\"",
						"cache-control": "no-cache",
						"postman-token": "d71648ba-61f2-5293-e424-ec45e85ed4c7"
						},
					"processData": false,
					"data": "{ \n  \"currency\" : \"" + curr + "\" \n}"
				}

                $.ajax(settings).done(function (response) {
					for(var key2 in response){
						$('#todr').append( '<li><a href="#"><id=' + key2 + '">' + key2 + '</a></li>' );

						}
                    $("#todr li a").click(function(){
                        $("#toDropdownMenu:first-child").text($(this).text());
                        $("#toDropdownMenu:first-child").val($(this).text());
                    });
            });
        });
    });

    });

function movebar(){
	var elem = document.getElementById("bar");
	var width = 1;
	var id = setInterval(frame, 13);
	
	function frame(){
		if (width>= 100){
			clearInterval(id);
		} else{
				width++;
				elem.style.width = width + '%';
				elem.innerHTML = width * 1 + '%';
			}
	}

}

$("#days li a").click(function(){
    $("#daysDropdownMenu:first-child").text($(this).text());
    $("#daysDropdownMenu:first-child").val($(this).text());
});

$("#forecast").click(function(){
    var currfrom = ($("#fromDropdownMenu:first-child").val());
	var currto = ($("#toDropdownMenu:first-child").val());
    var days = ($("#daysDropdownMenu:first-child").val());

	if (!currfrom || !currto || !days){
		$("#result").removeClass('hidden');
		$("#result").removeClass('alert-success');
		$("#result").addClass('alert-danger')
		$("#result").text('All fileds need to be selected!');
		$("#result").fadeIn();
	}
	else {
		$("#result").addClass('hidden');
		$("#result").removeClass('alert-danger');
		$("#result").addClass('alert-success')
		$("#progressbar").removeClass('hidden');
		movebar();
		var settings = {
			"async": true,
			"crossDomain": true,
			"url": URL + "/forecast",
			"method": "POST",
			"headers": {
				"content-type": "application/json",
				"cache-control": "no-cache",
				"postman-token": "d0134958-b639-0d25-f0a6-838ca556c7e9"
			},
			"processData": false,
			"data": "{\n \"currencyfrom\": \"" + currfrom + "\",\n \"currencyto\": \"" + currto + "\",\n \"days\":" + days + "\n}"
		}

		$.ajax(settings).done(function (response) {
			$("#progressbar").fadeOut();
			var data = response['forecasts'];
			var poz = parseFloat(response['accuracy']).toFixed(2) * 100;
			var neg = 100 - poz;

			var piedata = [
				{label: 'Accuracy', value: poz},
				{label: 'Inaccuracy', value: neg}
			];
			console.log(piedata);
			$("#result").removeClass('hidden');
			$("#result").text('According to the forecast the best day to buy is: ' + response['tobuy'] + ' and to sell is: ' + response['tosell']);
			$("#result").fadeIn();


			Morris.Line({
				hideHover: false,
				element: 'placeholder',
				data: data,
				ymin: 'auto',
				xkey: 'x',
				ykeys: ['y'],
				labels: ['value']
			});

			Morris.Donut({
				formatter: function (y, data) {
					return y + '%'
				},
				element: 'pie',
				hideHover: 'auto',
				resize: true,
				data: piedata,
				colors: ['#1424b8', '#b83214']
			});

		});
	}
});
