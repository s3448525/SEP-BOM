
var Application = function() {

    var config = {};

    var startDate;
    var endDate;

    var loadCount = 0;


    function __init__(options) {
        $.extend(true, config, options);

        // Configure date range picker
        startDate = new Date;
        endDate = new Date;	// Today

        $('input[name="daterange"]').daterangepicker(
            {
                locale: {
                    format: 'MMMM DD, YYYY'
                },
                dateLimit: {
                    days: 7
                },
                startDate: startDate,
                endDate: endDate
            }, function (start, end, label) {
                console.log("A new date range was chosen: " + start.format('YYYY-MM-DD') + ' to ' + end.format('YYYY-MM-DD'));
                startDate = new Date(start.format('YYYY-MM-DD'));
                endDate = new Date(end.format('YYYY-MM-DD'));
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
            time = endDate.toISOString(),
            max_dist = 10000; // meters
        // alert() is only for debug
        if (location == '' || location == null) {
            alert("Please select a location");
            return;
        }

        // Update location name label
        document.getElementById("location-name-label").innerHTML =
            $('input[name="input_location"]').val().split(",")[0] + ", " + $('input[name="input_location"]').val().split(",")[1] + " at " + endDate.toString();

        // Display data table if hidden
        $('#result-table').show();

        // Clear previous content
        $('#loading').show();
        var data_table = $('#data-table').find('tbody');
        data_table.empty();
        data_table.hide();

        // Initiate requests for each day
        displayData(data_type, lat, lon, max_dist, endDate);
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
                    fc_unit = "%";
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

            // Display each forecast.
            // TODO: order forecasts by date.
            // TODO: collapse multiple forecasts from the same day, expandable by clicking.
            var observation_points = {};
            for (i = 0; i < data.data.length; i++) {
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
                }
                accuracy = "-"
                if (data.data[i].accuracy == true) {
                    accuracy = "<span style='color:#00FA00;'>✔</span>";
                } else {
                    accuracy = "<span style='color:#FA0000;'>✘</span>";
                }
                // Display the result.
                data_table.append("<tr>" +
                    "<td>" + data.data[i].forecast_creation_date + "</td>" +
                    "<td>" + data.data[i].forecast.value.toString() + fc_unit + "</td>" +
                    "<td>" + obs_value_min + " - " + obs_value_max + " " + ob_unit + "</td>" +
                    "<td>" + accuracy + "</td>" +
                    "</tr>");
            }

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
