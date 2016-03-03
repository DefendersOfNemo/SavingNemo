alert("Here");
$(function() {
        $( "#date_pick_from" ).datepicker({
          defaultDate: "+1w",
          changeMonth: true,
          changeYear: true,
          numberOfMonths: 2,
          onClose: function( selectedDate ) {
            $( "#date_pick_to" ).datepicker( "option", "minDate", selectedDate );
          }
        });
        $( "#date_pick_to" ).datepicker({
          defaultDate: "+1w",
          changeMonth: true,
          changeYear: true,
          numberOfMonths: 2,
          onClose: function( selectedDate ) {
            $( "#date_pick_from" ).datepicker( "option", "maxDate", selectedDate );
          }
        });
        
        $('#state_name').click( function () {
          state_name = $("#state_name option:selected").text();
          $.getJSON('/_parse_data', {
            select_type: "state_name",
            select_value: state_name
            }, function(data) {
            var options = $("#location_name");
            options.empty();
            $.each(data, function() {
              options.append($("<option />").val(this).text(this));
            });
          });
        });

        $('#dropdown_menu_logger_type').change( function () {
          logger_type = $("#dropdown_menu_logger_type option:selected").text();
          alert(logger_type)
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
          alert(country_name)
          $.getJSON('/_parse_data', {
            select_type: "country_name",
            select_value: country_name
            }, function(data) {
            $('#dropdown_menu_state_name').empty()
            $.each(data, function(state) {
              $("#dropdown_menu_state_name").append('<option value=\"'+state+'\">'+state+'</option>')
            });
          });
        });
        
        $('#country_name').click( function () {
          /*country_name = $(this).text();*/
          country_name = $("#country_name option:selected").text();
          /*$('.db_country_name').text(country_name).append(' <span class="caret"/>');    */
          $.getJSON('/_parse_data', {
            select_type: "country_name",
            select_value: country_name
            }, function(data) {
            var options = $("#state_name");
            $.each(data, function() {
              options.append($("<option />").val(this).text(this));
            });
          });
        });




        $('#logger_type').click( function () {
          logger_type = $("#logger_type option:selected").text();
            $.getJSON('/_parse_data', {
                    select_type: "logger_type",
                    select_value: logger_type
                  })
            .done(function(data){              
              $('#country_name').empty()
              $.each(data, function(country){ 
                $("#country_name").append($("<option />").val(this).text(this));             
              });
            });
            $.getJSON('/_parse_data', {
              select_type: "lt_for_zone",
              select_value: logger_type
              }, function(data) {
              var options = $("#zone_name");
              options.empty();
              $.each(data, function() {
                options.append($("<option />").val(this).text(this));
              });
            });
            
            $.getJSON('/_parse_data', {
              select_type: "lt_for_subzone",
              select_value: logger_type
              }, function(data) {
              var options = $("#sub_zone_name");
              options.empty();
              $.each(data, function() {
                options.append($("<option />").val(this).text(this));
              });
            });

            $.getJSON('/_parse_data', {
              select_type: "lt_for_wave_exp",
              select_value: logger_type
              }, function(data) {
              var options = $("#wave_exp_name");
              options.empty();
              $.each(data, function() {
                options.append($("<option />").val(this).text(this));
              });
            });

        });

        /*$('#button_submit').click( function () {
          
          form_data = $('form[name="query"]')
          alert(form_data)
            $.getJSON('/_parse_data', {
                    select_type: "logger_type",
                    select_value: logger_type
                  })
            .done(function(data){              
              $('#country_name').empty()
              $.each(data, function(country){ 
                $("#country_name").append($("<option />").val(this).text(this));             
              });
            });*/
    });
