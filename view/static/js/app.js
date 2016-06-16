
var Application = function() {

    var config = {};

    var chosenDate;

    var sub_day_forecasts = {};


    function __init__(options) {
        $.extend(true, config, options);

        // Configure date picker.
        // TODO turn the date/time picker into a slider bar instead of a select.
        var currentDate = new Date();	// Today
        currentDate.setHours(currentDate.getHours() - (currentDate.getHours() % 3));
        currentDate.setMinutes(0);
        currentDate.setSeconds(0);
        currentDate.setMilliseconds(0);
        var earliestDate = currentDate.getTime() - (7*24*60*60*1000);
        var datePicker = $('#date-picker');
        for (var i = currentDate.getTime(); i > earliestDate; i -= (3*60*60*1000)) {
            var optionDate = moment(i);
            datePicker.append($('<option>', {value:optionDate.toISOString(), text:optionDate.format('DD/MM/YYYY, hh:mm:ss A')}));
        }
        chosenDate = new Date(datePicker.val());

        datePicker.on( "change", function(){
            chosenDate = new Date($(this).val());
            search();
        });

        $('#button-search').off().on('click', search);
        $('#observation-source').on('change', search);
    }

    function search() {
        // Feva API call to retrieve JSON object
        var e = document.getElementById("select-data-type"),
            data_type = e.options[e.selectedIndex].value,
            coords = $('input[name="input_location_coord"]').val().split(","),
            location = $('input[name="input_location"]').val(),
            obs_source = $('#observation-source').val(),
            time = chosenDate.toISOString(),
            max_dist = 10000; // meters
        var lat = coords[0], lon = coords[1];
        // alert() is only for debug
        if (location == '' || location == null) {
            alert("Please select a location");
            return;
        }

        // Update location name label
        var displayChosenDate = moment(chosenDate.getTime());
        $("#location-name-label").html(
            location.split(",")[0] + ", " +location.split(",")[1] +
            ", " + displayChosenDate.calendar(null, {'sameElse':'ddd MMM D [at] ha'}));

        // Display data table if hidden
        $('#result-table').show();

        // Clear previous content
        $('#loading').show();
        var data_table = $('#data-table').find('tbody');
        data_table.empty();
        data_table.hide();
        $('#observation-summary').empty();

        // Initiate requests for each day
        displayData(data_type, lat, lon, max_dist, chosenDate, obs_source);
    }

    // Call API/evaluate to get evaluation data.
    function evaluateForecasts(data_type, lat, lon, max_dist, time, obs_source, callback) {
        console.log(data_type, lat, lon, max_dist, time);
        $.getJSON('api/evaluate/', {
            weather_type: data_type,
            latitude: lat,
            longitude: lon,
            max_distance: max_dist,
            time: time.toISOString(),
            obs_source: obs_source
        }, function (data) {
            callback(data);
        });
    }

    // Display returned API data and populate the data table
    function displayData(data_type, lat, lon, max_dist, time, obs_source) {
        //get our JSON
        evaluateForecasts(data_type, lat, lon, max_dist, time, obs_source, function (data) {
            var data_table = $('#data-table').find('tbody');
            data_table.empty();
            sub_day_forecasts = {};

            //
            if (data.success != true) {
                // Display error
                console.log(data);
                data_table.append("<tr><td colspan='4'>Data Unavailable</td></tr>");
                $('#loading').hide();
                data_table.fadeIn(500);
                return;
            }

            // Determine measurement units.
            var fc_unit = "", ob_unit = "";
            switch (data_type) {
                case "rain":
                    fc_unit = "% chance of rain";
                    ob_unit = "mm";
                    break;
                case "temperature":
                    fc_unit = "°C";
                    ob_unit = "°C";
                    break;
                case "wind_speed":
                    fc_unit = "km/h";
                    ob_unit = "km/h";
                    break;
                default:
                    break;
            }
            console.log(data);

            // Sort results by forecast_creation_date.
            data.data.sort(function(a,b){
                return new Date(b.forecast.creation_date).getTime() - new Date(a.forecast.creation_date).getTime()
            });

            // Display each forecast.
            // TODO: order forecasts by date.
            // TODO: collapse multiple forecasts from the same day, expandable by clicking.
            var overall_obs_min = 0;
            var overall_obs_max = 0;
            var observation_points = {};
            var prev_day = '';
            for (i = 0; i < data.data.length; i++) {
                var fc_creation_date = moment.utc(data.data[i].forecast.creation_date);
                fc_creation_date.local();
                console.log(fc_creation_date.toISOString());
                var observations = data.data[i].observations;
                var obs_value_min, obs_value_max;
                for (j = 0; j < observations.length; j++) {
                    // Prepare observations to be marked on the map.
                    var key = observations[j].location[0]+","+observations[j].location[1];
                    if (!(key in observation_points)) {
                        observation_points[key] = [observations[j].value.toString()+ob_unit,
                            observations[j].location[0],
                            observations[j].location[1]];
                    } else {
                        observation_points[key][0] += ", "+observations[j].value.toString()+ob_unit;
                    }
                    // Find the minimum observation.
                    if (j == 0 || observations[j].value < obs_value_min)
                        obs_value_min = observations[j].value;
                    // Find the maximum observation.
                    if (j == 0 || observations[j].value > obs_value_max)
                        obs_value_max = observations[j].value;
                    // Find the overall minimum observation.
                    if (j == 0 || observations[j].value < overall_obs_min)
                        overall_obs_min = observations[j].value;
                    // Find the overall maximum observation.
                    if (j == 0 || observations[j].value > overall_obs_max)
                        overall_obs_max = observations[j].value;
                }
                var accuracy = "-";
                if (data.data[i].accuracy == true) {
                    accuracy = '<i class="fa fa-check result-correct" aria-hidden="true"></i>';
                } else {
                    accuracy = '<i class="fa fa-times result-incorrect" aria-hidden="true"></i>';
                }
                // Display the result.
                var date = $('<td>');
                var forecast_value = $('<td>');
                var forecast_result = $('<td>');
                var evaluation = $('<td>');

                date.html('<span class="forecast-issued">Issued </span>' + fc_creation_date.from(time, true) + ' before');
                forecast_value.html(data.data[i].forecast_value.value.toString() + fc_unit);
                forecast_result.html("Observed " + obs_value_min + " - " + obs_value_max + " " + ob_unit);
                evaluation.html(accuracy);

                var row = $('<tr>');

                row.append(date).append(forecast_value).append(forecast_result).append(evaluation);
                data_table.append(row);
                date.tooltip({
                    container: 'body',
                    title: fc_creation_date.format('MMM Do YYYY, [at] hh:mm A'),
                    placement: 'top'
                });
            }

            // Display overall observation summary.
            $('#observation-summary').html(overall_obs_min+" - "+overall_obs_max+" "+ ob_unit);

            // Display observation points on the map.
            var observation_points_list = [];
            for (var point in observation_points) {
                observation_points_list.push(observation_points[point]);
            }
            addMarkers(map, observation_points_list);

            // Hide the loading bar, show the results.
            $('#loading').hide();
            data_table.fadeIn(500);
        });
    }


    return {
        init: __init__,
        search: search
    }
};
