/*
 * Django-CIVIL
 *
 * Running code to allow better handling of fields in change list/form
 */

(function($) {

    var updateContributionVisibility = function() {
        var selected = $("#id_period").val();
        if (selected == 1) {
            $("fieldset.module:eq(1)").hide();
            $("fieldset.module:eq(2)").show();
        }else{
            $("fieldset.module:eq(1)").show();
            $("fieldset.module:eq(2)").hide();
        }
    };

    $(document).ready(function(){
        if ($("#changelist-form").length) // exists
        {
            // we are in change_list
        }
        else
        {
            // we are in change_form
            updateContributionVisibility();

            $("#id_period").change(function(e) {
                updateContributionVisibility();
            });
        }
    });
    
}(django.jQuery));
