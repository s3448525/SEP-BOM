
var Application = function() {

    var config = {};

    var startDate;
    var endDate;


    function __init__(options) {
        $.extend(true, config, options);

        // Configure date range picker
        startDate = new Date(new Date().setDate(new Date().getDate() - 7));
        endDate = new Date;	// Today

        $('input[name="daterange"]').daterangepicker(
            {
                locale: {
                    format: 'YYYY-MM-DD'
                },
                "dateLimit": {
                    "days": 7
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
        } else {
            alert("Latitude: " + lat + "\n" +
                "Longitude: " + lon + "\n" +
                "Type: " + data_type + "\n" +
                "Max Distance: " + max_dist + "\n" +
                "Time: " + time
            );
        }

        // Update location name label
        document.getElementById("location-name-label").innerHTML =
            $('input[name="input_location"]').val().split(",")[0] + ", " + $('input[name="input_location"]').val().split(",")[1];

        // Display data table if hidden
        $('#data-table').collapse("show");

        // Clear previous content
        var data_table = document.getElementById("data-table");
        for (i = 1; data_table.rows.length - i > 0;) {
            data_table.deleteRow(data_table.rows.length - i);
        }

        // Calculate how many days of data to lookup
        var time_span = Math.ceil(Math.abs(endDate.getTime() - startDate.getTime()) / (1000 * 3600 * 24)) + 1;
        for (i = 1; i <= time_span; i++) {
            tr = data_table.insertRow(i);
            tr.id = "data-table-content-row-" + i;
        }

        // Initiate requests for each day
        for (i = 0; i < time_span; i++) {
            time = new Date((new Date).setDate(endDate.getDate() - i));
            displayData(data_type, lat, lon, max_dist, time, i + 1);
        }
    }

    // Send API calls
    function makeAPICalls(data_type, lat, lon, max_dist, time, callback) {
        // Send search request
        console.log(data_type, lat, lon, max_dist, time);
        var temp = $.getJSON('api/evaluate', {
            weather_type: data_type,
            latitude: lat,
            longitude: lon,
            max_distance: max_dist,
            time: time.toISOString()//.substring(0, 10) + "T04\:00\:00\.0Z"
        }, function (data) {
            callback(data);
        });
    }

    // Display returned API data and populate the data table
    function displayData(data_type, lat, lon, max_dist, time, row_number) {
        //get our JSON
        makeAPICalls(data_type, lat, lon, max_dist, time, function (data) {
            //when we get our data, evaluate
            // console.log(time);
            if (data.success == true) {
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
                // Get returned data average
                var observation_points = [];
                var forecast_value_average = 0, observation_value_average = 0;
                for (i = 0; i < data.data.length; i++) {
                    forecast_value_average += data.data[i].forecast.value;
                    observation_value_average += data.data[i].observation.value;
                    observation_points[i] = [data.data[i].observation.value.toString(),
                        data.data[i].observation.location[0],
                        data.data[i].observation.location[1]];
                }
                forecast_value_average = (forecast_value_average / data.data.length).toFixed(2);
                observation_value_average = (observation_value_average / data.data.length).toFixed(2);
                accuracy = "-"
                if (data.data[0].accuracy == true) {
                    accuracy = "<span style='color:#00FA00;'>✔</span>";
                } else {
                    accuracy = "<span style='color:#FA0000;'>✘</span>";
                }
                //addMarkers(map, observation_points);
                // Display valid data
                document.getElementById("data-table-content-row-" + row_number).innerHTML =
                    "<td>" + new Date(time).toString().substring(4, 10) + "</td>" +
                    "<td>" + data.data[0].forecast.value.toString() + fc_unit + "</td>" +
                    "<td>" + data.data[0].observation.value.toString() + ob_unit + "</td>" +
                    "<td>" + accuracy + "</td>";
            } else {
                // Display error
                console.log(data);
                // console.log(new Date(time).toString().substring(0, 10));
                document.getElementById("data-table-content-row-" + row_number).innerHTML =
                    "<td>" + new Date(time).toString().substring(4, 10) + "</td>" +
                    "<td>" + "no data" + "</td>" +
                    "<td>" + "no data" + "</td>" +
                    "<td>" + "-" + "</td>";
            }
        });
    }

    // Make API call to get
    function getObservations(lat, lon, max_dist) {
        // Send search request
        var temp = $.getJSON('/api/locations/observations', {
            latitude: lat,
            longitude: lon,
            max_distance: max_dist,
            limit: 99999999
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