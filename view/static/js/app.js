
var Application = function() {

    var config = {};

//    var startDate;
    var chosenDate;

    var loadCount = 0;
    var sub_day_forecasts = {}


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
        for (var i = currentDate.getTime(); i > earliestDate; i -= (3*60*60*1000)) {
            var optionDate = new Date(i);
            $('#date-picker').append($('<option>', {value:optionDate.toISOString(), text:optionDate.toLocaleString()}));
        }
        chosenDate = new Date($('#date-picker').val());

        $('#date-picker').on( "change", function(){
            chosenDate = new Date($('#date-picker').val());
            search();
        });

        $('#button-search').off().on('click', search);
    }

    function search() {
        // Feva API call to retrieve JSON object
        var e = document.getElementById("select-data-type"),
            data_type = e.options[e.selectedIndex].value,
            lat = $('input[name="input_location_coord"]').val().split(",")[0],
            lon = $('input[name="input_location_coord"]').val().split(",")[1],
            location = $('input[name="input_location"]').val(),
            time = chosenDate.toISOString(),
            max_dist = 10000; // meters
        // alert() is only for debug
        if (location == '' || location == null) {
            alert("Please select a location");
            return;
        }

        // Update location name label
        var displayChosenDate = moment.utc(chosenDate.toISOString());
        displayChosenDate.local();
        document.getElementById("location-name-label").innerHTML =
            $('input[name="input_location"]').val().split(",")[0] +
            ", " + $('input[name="input_location"]').val().split(",")[1] +
            ", " + displayChosenDate.calendar(null, {'sameElse':'ddd MMM D [at] ha'});

        // Display data table if hidden
        $('#result-table').show();

        // Clear previous content
        $('#loading').show();
        var data_table = $('#data-table').find('tbody');
        data_table.empty();
        data_table.hide();
        $('#observation-summary').empty();

        // Initiate requests for each day
        displayData(data_type, lat, lon, max_dist, chosenDate);
    }

    // Call API/evaluate to get evaluation data.
    function evaluateForecasts(data_type, lat, lon, max_dist, time, callback) {
        console.log(data_type, lat, lon, max_dist, time);
        $.getJSON('api/evaluate/', {
            weather_type: data_type,
            latitude: lat,
            longitude: lon,
            max_distance: max_dist,
            time: time.toISOString()
        }, function (data) {
            callback(data);
        });
    }

    // Display returned API data and populate the data table
    function displayData(data_type, lat, lon, max_dist, time) {
        //get our JSON
        evaluateForecasts(data_type, lat, lon, max_dist, time, function (data) {
            var data_table = $('#data-table').find('tbody');
            data_table.empty();
            sub_day_forecasts = {};

            // console.log(time);
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
                return new Date(b.forecast_creation_date).getTime() - new Date(a.forecast_creation_date).getTime()
            });

            // Display each forecast.
            // TODO: order forecasts by date.
            // TODO: collapse multiple forecasts from the same day, expandable by clicking.
            var overall_obs_min = 0;
            var overall_obs_max = 0;
            var observation_points = {};
            var prev_day = '';
            for (i = 0; i < data.data.length; i++) {
                var fc_creation_date = moment.utc(data.data[i].forecast_creation_date);
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
                accuracy = "-"
                if (data.data[i].accuracy == true) {
                    accuracy = "<span style='color:#00FA00;'>✔</span>";
                } else {
                    accuracy = "<span style='color:#FA0000;'>✘</span>";
                }
                // Hide all but one forecast for each day.
                var fc_creation_day = fc_creation_date.format('YYYYMMDD');
                if (fc_creation_day != prev_day) {
                    // First row of this day.
                }
                // Display the result.
                data_table.append("<tr>" +
                    "<td><div style='font-size:14pt;display:inline-block;'><span style='color:#808080;'>Issued</span> " + fc_creation_date.calendar(null, {'sameElse':'ddd MMM D [at] ha'}) + "</div>" +
                    "<div style='font-size:14pt;display:inline-block;'><span style='margin:0em 2em;'>" + data.data[i].forecast.value.toString() + fc_unit + "</span>" +
                    "<span style='font-size:18pt;'>" + accuracy + "</span></div>" +
                    "<div style='font-size:10pt;color:#808080;'>Observations for this period: " +obs_value_min + " - " + obs_value_max + " " + ob_unit + "</div>" +
                    "</td></tr>");
                console.log(fc_creation_day);
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

    // Make API call to get
    function getObservations(lat, lon, max_dist) {
        return;
        // Send search request
        var temp = $.getJSON('/api/locations/observations', {
            latitude: lat,
            longitude: lon,
            max_distance: max_dist,
            limit: 200
        }, function (data) {
            if (data.success == true) {
                var raw_data = data.data,
                    uniq_locations = new Set(),
                    uniq_locations_string = [];

                $.each(raw_data, function (index, value) {
                    coord = value.location[0].toString() + "," + value.location[1].toString();
                    if ($.inArray(coord, uniq_locations_string) == -1) {
                        uniq_locations.add(value.location);
                        uniq_locations_string.push(coord);
                    }
                });

                uniq_locations = Array.from(uniq_locations);
                observation_locations = [];
                $.each(uniq_locations, function (index, value) {
                    uniq_locations[index].splice(0, 0, raw_data[index].value.toString());
                    observation_locations.push(uniq_locations[index]);
                });

                addMarkers(map, observation_locations);
                // showMarkers();
                // console.log("current number of observation points: " + uniq_locations.length);
                document.getElementById("obs_count").innerHTML = uniq_locations.length;
            }
        });
    }


    return {
        init: __init__,
        search: search,
        getObservations: getObservations
    }
};
