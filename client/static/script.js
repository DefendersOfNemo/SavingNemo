$(function() {
    $( "#date_pick_from" ).datepicker({
        defaultDate: "+1w",
        changeMonth: true,
        changeYear: true,
        numberOfMonths: 1,
        onClose: function( selectedDate ) {
            $( "#date_pick_to" ).datepicker( "option", "minDate", selectedDate );
        }
    });
    
    $( "#date_pick_to" ).datepicker({
        defaultDate: "+1w",
        changeMonth: true,
        changeYear: true,
        numberOfMonths: 1,
        onClose: function( selectedDate ) {
            $( "#date_pick_from" ).datepicker( "option", "maxDate", selectedDate );
        }
        });

    $('#dropdown_menu_logger_type').change( function () {
        logger_type = $("#dropdown_menu_logger_type option:selected").text();
        $.getJSON('/_parse_data', {
            select_type: "logger_type",
            select_value: logger_type
        })
        .done(function(data){              
            $('#dropdown_menu_country_name').empty();
            $("#dropdown_menu_country_name").append('<option value="-1">Please select Country Name</option>')
            $.each(data, function(country){ 
                $("#dropdown_menu_country_name").append('<option value=\"'+country+'\">'+country+'</option>')
            });
        });
    });
    
    $('#dropdown_menu_country_name').change( function () {
        country_name = $("#dropdown_menu_country_name option:selected").text();
        $.getJSON('/_parse_data', {
            select_type: "country_name",
            select_value: country_name
        }).done(function(data) {
            $('#dropdown_menu_state_name').empty()
            $("#dropdown_menu_state_name").append('<option value="-1">Please select State Name</option>')
            $.each(data, function(state) {
                $("#dropdown_menu_state_name").append('<option value=\"'+state+'\">'+state+'</option>')
            });
        });
    });
    
    $('#dropdown_menu_state_name').change( function () {
        state_name = $("#dropdown_menu_state_name option:selected").text();
        $.getJSON('/_parse_data', {
            select_type: "state_name",
            select_value: state_name
            }).done(function(data) {
            $('#dropdown_menu_location_name').empty()
            $("#dropdown_menu_location_name").append('<option value="-1">Please select Location Name</option>')
            $.each(data, function(location) {
                $("#dropdown_menu_location_name").append('<option value=\"'+location+'\">'+location+'</option>')
            });
        });
    });
    
    $('#dropdown_menu_location_name').change( function () {
        location_name = $("#dropdown_menu_location_name option:selected").text();
        $.getJSON('/_parse_data', {
            select_type: "lt_for_zone",
            select_value: logger_type
        }).done(function(data) {
            $('#dropdown_menu_zone_name').empty()
            $("#dropdown_menu_zone_name").append('<option value="-1">Please select Zone Name</option>')
            $.each(data, function(zone) {
                $("#dropdown_menu_zone_name").append('<option value=\"'+zone+'\">'+zone+'</option>')
            });
        });
    });
    
    $('#dropdown_menu_zone_name').change( function () {
        zone_name = $("#dropdown_menu_zone_name option:selected").text();
        $.getJSON('/_parse_data', {
            select_type: "lt_for_subzone",
            select_value: logger_type
            }).done(function(data) {
            $('#dropdown_menu_sub_zone_name').empty()
            $("#dropdown_menu_sub_zone_name").append('<option value="-1">Please select Sub zone</option>')
            $.each(data, function(sub_zone) {
                $("#dropdown_menu_sub_zone_name").append('<option value=\"'+sub_zone+'\">'+sub_zone+'</option>')
            });
        });
    });
        
    $('#dropdown_menu_sub_zone_name').change( function () {
        sub_zone_name = $("#dropdown_menu_sub_zone_name option:selected").text();
        $.getJSON('/_parse_data', {
            select_type: "lt_for_wave_exp",
            select_value: logger_type
            }).done(function(data) {
            $('#dropdown_menu_wave_exp_name').empty()
            $("#dropdown_menu_wave_exp_name").append('<option value="-1">Please select wave exposure </option>')
            $.each(data, function(wave_exp) {
                $("#dropdown_menu_wave_exp_name").append('<option value=\"'+wave_exp+'\">'+wave_exp+'</option>')
            });
        });
    });

    $('#button_submit_query').click(function () {                   
        $.getJSON('/_submit_query', {
            logger_type: $("#dropdown_menu_logger_type option:selected").text(),
            country_name: $("#dropdown_menu_country_name option:selected").text(),
            state_name: $("#dropdown_menu_state_name option:selected").text(),
            location_name: $("#dropdown_menu_location_name option:selected").text(),
            zone_name: $("#dropdown_menu_zone_name option:selected").text(),
            sub_zone_name: $("#dropdown_menu_sub_zone_name option:selected").text(),
            wave_exp: $("#dropdown_menu_wave_exp_name option:selected").text(),
            start_date: $("#date_pick_from").val(),
            end_date: $("#date_pick_to").val(),
        })
        .done(function(data){
            console.log(data.list_of_results)
            var options = $("#query-results-table");
            $("#collapse1").toggleClass('collapse');
            options.empty()
            options.append("<tbody>")
            $.each(data.list_of_results, function(key, value) {
                options.append("<tr><td>"+value[0]+"</td><td>"+value[1]+"</td></tr>")
            });
            options.append("</tbody>")
        });
    });
});

