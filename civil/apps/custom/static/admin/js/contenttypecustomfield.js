/*
 * Django-CIVIL
 *
 * Running code to allow better handling of fields in change list/form
 */

(function($) {

    var updateDatatypeVisibility = function() {
        var selected = $("#id_datatype").val();
        switch (selected) {
          case "text":
            $("fieldset.module:eq(2)").show();
            $("fieldset.module:eq(3)").hide();
            break;
          case "int":
          case "float":
            $("fieldset.module:eq(2)").hide();
            $("fieldset.module:eq(3)").show();
            break;
          case "decimal":
            $("fieldset.module:eq(2)").hide();
            $("fieldset.module:eq(3)").hide();
            break;
          default:
            $("fieldset.module:eq(2)").hide();
            $("fieldset.module:eq(3)").hide();
            break;
        }
    };

    $(document).ready(function(){
        if ($("#changelist-form").length) // exists
        {
            // we are in change_list
        }
        else
        {
            // we are in change_form / view_form
            updateDatatypeVisibility();

            $("#id_datatype").change(function(e) {
                updateDatatypeVisibility();
            });
        }
    });
    
}(django.jQuery));
