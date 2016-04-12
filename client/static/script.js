$(function() {
    $('#dropdown_menu_biomimic_type').change( function () {
        biomimic_type = $("#dropdown_menu_biomimic_type option:selected").text();
        $('#dropdown_menu_country_name').empty();
        $('#dropdown_menu_state_name').empty();
        $('#dropdown_menu_location_name').empty();
        $('#dropdown_menu_zone_name').empty();
        $('#dropdown_menu_sub_zone_name').empty();
        $('#dropdown_menu_wave_exp_name').empty();
        $("#date_pick_from").datepicker('setDate', null);
        $("#date_pick_to").datepicker('setDate', null);
        $("#frequency-select").empty()
        $('#dropdown_menu_output_type_name').prop('selectedIndex', "Raw");
        // loading start
        $("#spinner-biomimic").show();
        $.getJSON('/_parse_data', {
            select_type: "biomimic_type",
            select_value: biomimic_type
        })
        .done(function(data){    
            var result = data["result"]
            var country_list = result["country"]
            var zone_list = result["zone"]
            // loading end
            $("#spinner-biomimic").hide();
            // update metadata field
            $('#selected-metadata').empty();
            if (data["countRecords"] != null){                
                $('#selected-metadata').removeClass('alert-danger');
                $('#selected-metadata').addClass('alert-success');
                $('#selected-metadata').append('<strong>' + data["countRecords"] + ' Records Found</strong>' + '<br>Min. Date Range: ' + data["minDate"] + '<br>Max. Date Range: ' + data["maxDate"]);
            }
            else{
                $('#selected-metadata').removeClass('alert-success');
                $('#selected-metadata').addClass('alert-danger');
                $('#selected-metadata').append('<strong>Zero Records Found for Current Selection!</strong>');   
            }
            // update country field
            $("#dropdown_menu_country_name").append('<option value="">Please select Country Name</option>')
            $.each(country_list, function(index, country){
                $("#dropdown_menu_country_name").append('<option value=\"' + country + '\">' + country + '</option>')
            });
            // update zone field
            $("#dropdown_menu_zone_name").append('<option value="">Please select Zone Name</option>')
            $("#dropdown_menu_zone_name").append('<option value="1">All</option>')
            $.each(zone_list, function(index, zone){
                $("#dropdown_menu_zone_name").append('<option value=\"' + zone + '\">' + zone + '</option>')
            });
        });
    });
    
    $('#dropdown_menu_country_name').change( function () {
        country = $("#dropdown_menu_country_name option:selected").val();
        $('#dropdown_menu_state_name').empty();
        $('#dropdown_menu_location_name').empty();
        $('#dropdown_menu_sub_zone_name').empty();
        $('#dropdown_menu_wave_exp_name').empty();
        $("#date_pick_from").datepicker('setDate', null);
        $("#date_pick_to").datepicker('setDate', null);
        $("#frequency-select").empty()
        $('#dropdown_menu_output_type_name').prop('selectedIndex', "Raw");
        $("#spinner-country").show();
        $.getJSON('/_parse_data', {
            select_type: "country",
            select_value: country
        }).done(function(data) {
            $("#spinner-country").hide();            
            // update metadata field
            $('#selected-metadata').empty();
            if (data["countRecords"] != null){                
                $('#selected-metadata').removeClass('alert-danger');
                $('#selected-metadata').addClass('alert-success');
                $('#selected-metadata').append('<strong>' + data["countRecords"] + ' Records Found</strong>' + '<br>Min. Date Range: ' + data["minDate"] + '<br>Max. Date Range: ' + data["maxDate"]);
            }
            else{
                $('#selected-metadata').removeClass('alert-success');
                $('#selected-metadata').addClass('alert-danger');
                $('#selected-metadata').append('<strong>Zero Records Found for Current Selection!</strong>');   
            }
            // update state_province field
            var result = data["result"]
            $("#dropdown_menu_state_name").append('<option value="">Please select State Name</option>')
            $.each(result, function(index, state_province) {
                $("#dropdown_menu_state_name").append('<option value=\"' + state_province + '\">' + state_province + '</option>')
            });
        });
    });
    
    $('#dropdown_menu_state_name').change( function () {
        state_province = $("#dropdown_menu_state_name option:selected").text();
        $('#dropdown_menu_location_name').empty();
        $('#dropdown_menu_sub_zone_name').empty()
        $('#dropdown_menu_wave_exp_name').empty()
        $("#date_pick_from").datepicker('setDate', null);
        $("#date_pick_to").datepicker('setDate', null);
        $("#frequency-select").empty()
        $('#dropdown_menu_output_type_name').prop('selectedIndex', "Raw");
        $("#spinner-state").show();
        $.getJSON('/_parse_data', {
            select_type: "state_province",
            select_value: state_province
            })
        .done(function(data) {
            $("#spinner-state").hide();            
            // update metadata field
            $('#selected-metadata').empty();
            if (data["countRecords"] != null){                
                $('#selected-metadata').removeClass('alert-danger');
                $('#selected-metadata').addClass('alert-success');
                $('#selected-metadata').append('<strong>' + data["countRecords"] + ' Records Found</strong>' + '<br>Min. Date Range: ' + data["minDate"] + '<br>Max. Date Range: ' + data["maxDate"]);
            }
            else{
                $('#selected-metadata').removeClass('alert-success');
                $('#selected-metadata').addClass('alert-danger');
                $('#selected-metadata').append('<strong>Zero Records Found for Current Selection!</strong>');   
            }
            // update location field
            var result = data["result"]
            $("#dropdown_menu_location_name").append('<option value="">Please select Location Name</option>')
            $.each(result, function(index, location) {
                $("#dropdown_menu_location_name").append('<option value=\"' + location + '\">' + location + '</option>')
            });
        });
    });
    
    $('#dropdown_menu_location_name').change( function () {
        $("#date_pick_from").datepicker('setDate', null);
        $("#date_pick_to").datepicker('setDate', null);
        $('#dropdown_menu_sub_zone_name').empty()
        $('#dropdown_menu_wave_exp_name').empty()
        $("#frequency-select").empty()
        $('#dropdown_menu_output_type_name').prop('selectedIndex', "Raw");        
        $("#spinner-location").show();
        loc = $("#dropdown_menu_location_name option:selected").text();
        $.getJSON('/_parse_data', {
            select_type: "location",
            select_value: loc
            })
        .done(function(data) {
            $("#spinner-location").hide();            
            // update metadata
            $('#selected-metadata').empty();
            if (data["countRecords"] != null){                
                $('#selected-metadata').removeClass('alert-danger');
                $('#selected-metadata').addClass('alert-success');
                $('#selected-metadata').append('<strong>' + data["countRecords"] + ' Records Found</strong>' + '<br>Min. Date Range: ' + data["minDate"] + '<br>Max. Date Range: ' + data["maxDate"]);
            }
            else{
                $('#selected-metadata').removeClass('alert-success');
                $('#selected-metadata').addClass('alert-danger');
                $('#selected-metadata').append('<strong>Zero Records Found for Current Selection!</strong>');   
            }
        });        
    });
    
    $('#dropdown_menu_zone_name').change( function () {
        zone_type = $("#dropdown_menu_zone_name option:selected").text();
        $('#dropdown_menu_sub_zone_name').empty()
        $('#dropdown_menu_wave_exp_name').empty()
        $("#date_pick_from").datepicker('setDate', null);
        $("#date_pick_to").datepicker('setDate', null);        
        $("#frequency-select").empty()
        $('#dropdown_menu_output_type_name').prop('selectedIndex', "Raw");
        $("#spinner-zone").show();        
        $.getJSON('/_parse_data', {
            select_type: "zone",
            select_value: zone_type
            })
        .done(function(data) {
            $("#spinner-zone").hide();            
            // update metadata field
            $('#selected-metadata').empty();
            if (data["countRecords"] != null){                
                $('#selected-metadata').removeClass('alert-danger');
                $('#selected-metadata').addClass('alert-success');
                $('#selected-metadata').append('<strong>' + data["countRecords"] + ' Records Found</strong>' + '<br>Min. Date Range: ' + data["minDate"] + '<br>Max. Date Range: ' + data["maxDate"]);
            }
            else{
                $('#selected-metadata').removeClass('alert-success');
                $('#selected-metadata').addClass('alert-danger');
                $('#selected-metadata').append('<strong>Zero Records Found for Current Selection!</strong>');   
            }
            // update sub_zone field
            var result = data["result"]
            $("#dropdown_menu_sub_zone_name").append('<option value="">Please select Sub Zone</option>')
            $("#dropdown_menu_sub_zone_name").append('<option value="1">All</option>')
            $.each(result, function(index, sub_zone) {
                $("#dropdown_menu_sub_zone_name").append('<option value=\"' + sub_zone + '\">' + sub_zone + '</option>')
            });
        });
    });
        
    $('#dropdown_menu_sub_zone_name').change( function () {
        sub_zone_type = $("#dropdown_menu_sub_zone_name option:selected").text();
        $("#date_pick_from").datepicker('setDate', null);
        $("#date_pick_to").datepicker('setDate', null);
        $('#dropdown_menu_wave_exp_name').empty()
        $("#frequency-select").empty()
        $('#dropdown_menu_output_type_name').prop('selectedIndex', "Raw");
        $("#spinner-sub-zone").show();        
        $.getJSON('/_parse_data', {
            select_type: "sub_zone",
            select_value: sub_zone_type
            })
        .done(function(data) {
            $("#spinner-sub-zone").hide();            
            // update metadata field
            $('#selected-metadata').empty();
            if (data["countRecords"] != null){                
                $('#selected-metadata').removeClass('alert-danger');
                $('#selected-metadata').addClass('alert-success');
                $('#selected-metadata').append('<strong>' + data["countRecords"] + ' Records Found</strong>' + '<br>Min. Date Range: ' + data["minDate"] + '<br>Max. Date Range: ' + data["maxDate"]);
            }
            else{
                $('#selected-metadata').removeClass('alert-success');
                $('#selected-metadata').addClass('alert-danger');
                $('#selected-metadata').append('<strong>Zero Records Found for Current Selection!</strong>');   
            }
            // update wave_exp field
            var result = data["result"]
            $("#dropdown_menu_wave_exp_name").append('<option value="">Please select Wave Exposure</option>')
            $("#dropdown_menu_wave_exp_name").append('<option value="1">All</option>')
            $.each(result, function(index, wave_exp) {
                $("#dropdown_menu_wave_exp_name").append('<option value=\"' + wave_exp + '\">' + wave_exp + '</option>')
            });
        });
    });

    $('#dropdown_menu_output_type_name').change( function () {
        var query_field10 = $("#dropdown_menu_output_type_name option:selected").text();
        var select2 = $("#dropdown_menu_analysis_type_name")
        var select = $("#frequency-select")
        select.empty();
        if (query_field10 == "Raw"){
            select.empty()         
        } else {
            select.empty()
            select.append('<label for="dropdown_menu_analysis_type_name">Temperature Frequency:</label>')
            select.append('<select id ="dropdown_menu_analysis_type_name" class="form-control"><option value="Daily">per Day</option><option value="Monthly">per Month and Year</option><option value="Yearly">per Year</option>')
            select.append('</select>')
        }
    });

    function fieldValidation(){
        var query_field1 = $("#dropdown_menu_biomimic_type option:selected").text()
        var query_field2 = $("#dropdown_menu_country_name option:selected").text()
        var query_field3 = $("#dropdown_menu_state_name option:selected").text()
        var query_field4 = $("#dropdown_menu_location_name option:selected").text()
        var query_field5 = $("#dropdown_menu_zone_name option:selected").text()
        var query_field6 = $("#dropdown_menu_zone_name option:selected")
        var query_field7 = $("#dropdown_menu_wave_exp_name option:selected").text()
        var isChecked = $("#date-checkbox").prop("checked")
        var query_field10 = $("#dropdown_menu_output_type_name option:selected").text()
        var query_field11 = $("#dropdown_menu_analysis_type_name option:selected").val()
        var valid = false
        if ((query_field1 != "Please select Biomimic Type") && 
            (query_field2 != "Please select Country Name") && 
            (query_field3 != "Please select State Name") && 
            (query_field4 != "Please select Location Name") && 
            (query_field5 != "Please select Zone Name") && 
            (query_field6 != "Please select Sub zone") && 
            (query_field7 != "Please select Wave Exposure")){
                if (isChecked){
                    var query_field8 = $("#date_pick_from").val()
                    var query_field9 = $("#date_pick_to").val()
                    var date_format = new RegExp (/\d{2}\/\d{2}\/\d{4}/)
                    var date1 = date_format.test(query_field8)
                    var date2 = date_format.test(query_field9)
                    valid = (query_field8 != '') && (query_field9 != '') && (date1) && (date2)
                }
                else{
                    valid = true
                }
        }
        return valid
    }

    function tableheader(){
        frequency = $("#dropdown_menu_analysis_type_name option:selected").val()
        var title = ""
        if (frequency == "Daily") {
            title = ("Date")
        } 
        else if (frequency == "Monthly") {
            title = ("Month, Year")
        }
        else if (frequency == "Yearly") {
            title = ("Year")
        }
        else {
            title = ("Timestamp")
        }
        return title        
    }
    

    $('#button_submit_query').click(function () {
        if (fieldValidation()){
            var $btn = $(this)
            $btn.button('loading')
            $.getJSON('/_submit_query', {
                biomimic_type: $("#dropdown_menu_biomimic_type option:selected").text(),
                country: $("#dropdown_menu_country_name option:selected").text(),
                state_province: $("#dropdown_menu_state_name option:selected").text(),
                location: $("#dropdown_menu_location_name option:selected").text(),
                zone: $("#dropdown_menu_zone_name option:selected").text(),
                sub_zone: $("#dropdown_menu_sub_zone_name option:selected").text(),
                wave_exp: $("#dropdown_menu_wave_exp_name option:selected").text(),
                start_date: $("#date_pick_from").val(),
                end_date: $("#date_pick_to").val(),
                output_type: $("#dropdown_menu_output_type_name option:selected").text(),
                analysis_type: $("#dropdown_menu_analysis_type_name option:selected").val()
            }) 
            .done(function(data){
                $btn.button('reset')
                var values = (data.list_of_results)
                var options = $("#hidden-table");
                var button = $("#download-button");
                var title = $("#title")
                if (values == ''){
                    button.empty()
                    title.empty()
                    options.empty()
                    var targetOffset = $("#hidden-table").offset().top - 50;
                    $('html,body').animate({scrollTop:targetOffset}, 750);
                    options.append("<h3 class=text-danger>  Search was unsucessful, please try again with different select options<h3>")
                } 
                else {
                    options.empty()
                    var targetOffset = $("#hidden-table").offset().top - 50;
                    $('html,body').animate({scrollTop:targetOffset}, 750);                    
                    title.empty()
                    title.append("<h4>Data preview</h4>")
                    options.append("<thead><tr><th>" + tableheader() + "</th><th>Temperature (in Celsius)</th></tr></thead><tbody>")
                    $.each(data.list_of_results, function(key, value) {
                        options.append("<tr><td>" + value[0] + "</td><td>" + value[1] + "</td></tr>")
                    });
                    options.append("</tbody>")
                        options.append("</table>")
                    button.empty()
                    button.append("<a href=\"/download\" class=\"btn btn-info btn-lg\" role=\"button\" autocomplete=\"off\"><span class=\"glyphicon glyphicon-download\"></span> Download All Data</a>")
                }
            });
        }
    });
    
    $('#date-checkbox').change(function() {
        var disableDateRange = !this.checked
        if (disableDateRange){
            $("#date_pick_from").datepicker('setDate', null);
            $("#date_pick_to").datepicker('setDate', null);
        }
        $("#date_pick_from").prop('disabled', disableDateRange);
        $("#date_pick_to").prop('disabled', disableDateRange);
    });

    $(document).ready(function(){
        // When the document is ready
        $("#alert").fadeTo(5000, 0).slideUp(500, function(){
            $(this).alert();    
        });
        $('[data-toggle="popover"]').popover(); 
        $('.input-daterange').datepicker({
            format: 'mm/dd/yyyy',
            todayHighlight: true,
            todayBtn: "linked",
            autoclose: true
        });
    });

    $("form").submit(function(e) {
        var validate = $(this).find("[required]");
        $(validate).each(function(){
            if ( $(this).val() == '' ){
                if (($(this).prop('id') != "date_pick_from") && ($(this).prop('id') != "date_pick_to")){
                    alert("Please fill all required fields");
                    $(this).focus();
                    e.preventDefault();
                    return false;
                }
                else{
                    if($("#date-checkbox").prop("checked")){
                        alert("Please fill all required fields");
                        $(this).focus();
                        e.preventDefault();
                        return false;       
                    }
                }
            }
        });    
        return true;
    });


});